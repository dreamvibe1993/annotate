import re
import os
import argparse
from typing import Dict

component_pattern = r"export\s+const\s\w+\s=.+JSX.Element\s=>\s{"
component_name_pattern = r"(?<=\s)[A-Z]\w+(?=\s=\s)"

type_pattern = r"type[^}]*};"
type_name_pattern = r"(?<=type\s)\w+(?=\s=\s)"
type_intersect_pattern = r"\w+(?=\s&)"
type_unions_pattern = r"\w+(?=\s\|)"
type_props_pattern = r"{([^}]*)}"

ts_class_pattern = r"export\sclass\s[A-Z]\w+[^{}]*{[^\r]+}"
class_name_pattern = r"(?<=class\s)\w+"

class_constructor_pattern = r"[^\n]+constructor\([^}]*\)\s{[^}]*}"
class_constructor_params_pattern = r"(?<=\()[^}]+(?=\)\s)"

class_method_pattern = r"\w+\s?\w+\([^}]*\):[^=\n]*?{"
class_method_name_pattern = r"\w+(?=\()"
method_params_pattern = r"(?<=\()[^\/]+(?=\):)"
method_param_type_pattern = r"(?<=:\s).+"
method_param_name_pattern = r"[\w?]+(?=:)"

func_type_param_pattern = r'\w+:\s\([^/]*\)\s=>\s\w+'

delimiter: str = "%%%%"

was_documented = False


def detect_if_was_documented(is_pristine: bool, content: str) -> bool:
	if is_pristine:
		print("Вы передали флаг -p. Смотрю был ли текущий файл документирован ранее...")
		return bool(re.search(r"/\*\*", content))
	return False


def we_have_name_and_type(param_name: "list[str]" or None, param_type: "list[str]" or None) -> bool: return len(
	param_type) > 0 and len(param_name) > 0


def get_type_and_name(pat: Dict[str, str], string_from: str) -> [str or None, str or None, bool]:
	param_type = re.findall(pat["type"], string_from)
	param_name = re.findall(pat["name"], string_from)
	if we_have_name_and_type(param_name, param_type):
		return [param_type[0], param_name[0].replace('?', ''), True]
	else:
		return [None, None, False]


def get_parameter_injected(param_type: str, param_name: str) -> str:
	return f"     * @param {{{param_type}}} {param_name} - \n"


def annotate_params(method_params: "list[str]") -> str:
	params_text = ""
	for line_of_methods_params in method_params:
		for func_type in re.findall(func_type_param_pattern, line_of_methods_params):
			parameter_of_func_type = re.sub(r":\s\(", delimiter + "(", func_type)
			func_param_name = parameter_of_func_type.split(delimiter)[0]
			func_param_type = parameter_of_func_type.split(delimiter)[1]
			params_text += get_parameter_injected(func_param_type, func_param_name)
			line_of_methods_params = line_of_methods_params.replace(func_type, "")
		if "," in line_of_methods_params:
			for param in line_of_methods_params.split(","):
				type_of_param, name_of_param, name_and_type_found = get_type_and_name({
					"name": method_param_name_pattern,
					"type": method_param_type_pattern
				}, param)
				if name_and_type_found:
					for generic in re.findall(r'<.+>', line_of_methods_params):
						type_without_generics = re.sub(r"<\w+>?", "", type_of_param)
						if type_without_generics + generic in line_of_methods_params:
							type_of_param = type_without_generics + generic
					params_text += get_parameter_injected(type_of_param, name_of_param)
		else:
			type_of_param, name_of_param, name_and_type_found = get_type_and_name({
				"name": method_param_name_pattern,
				"type": method_param_type_pattern
			}, line_of_methods_params)
			if name_and_type_found:
				params_text += get_parameter_injected(type_of_param, name_of_param)
	return params_text


def annotate_class(content: str) -> str:
	ts_classes: list[str] = re.findall(ts_class_pattern, content)
	for ts_class in ts_classes:
		content = content.replace(ts_class, "/** Описание класса */\n" + ts_class)

		class_constructor: list[str] = re.findall(class_constructor_pattern, ts_class)
		if class_constructor:
			class_constructor_params = re.findall(
				class_constructor_params_pattern, class_constructor[0])
			if len(class_constructor_params) > 0:
				constructor_annot_text = f'    /**\n{annotate_params(class_constructor_params)}     */\n'
				content = content.replace(
					class_constructor[0], constructor_annot_text + class_constructor[0])

		class_methods: list[str] = re.findall(class_method_pattern, ts_class)
		for class_method in class_methods:
			method_params = re.findall(method_params_pattern, class_method)
			params_annot_text = f"/**\n     * Описание метода\n{annotate_params(method_params)}     */\n"
			content = content.replace(
				class_method, params_annot_text + "    " + class_method)
			params_annot_text = ""
	return content


def annotate_component(content: str) -> str:
	components: list[str] = re.findall(component_pattern, content)
	for component in components:
		component_name_found = re.search(
			component_name_pattern, str(component)).group()
		content = content.replace(
			component,
			f"/**\n * Описание компонента\n * @param props {{@link {component_name_found}Props}}\n */\n{component}")
	return content


def add_annot_intersection_types(intersections: "list[str]") -> str:
	text = ''
	for intersection in intersections:
		link = f"@link {intersection.strip()}"
		text += f" * @see {{{link}}} \n"
	return text


# Склеивает функциональный тип из второго и третьего эл. массива
def join_func_type_or_return_default(prop_parts) -> str:
	return f"{prop_parts[1]}:{prop_parts[2]}"


def annotate_type_props(props: "list[str]") -> str:
	annotation_lines = []
	for prop in props:
		prop_lines = prop.split(";")
		for line in prop_lines:
			prop_parts = line.split(":")
			if len(prop_parts) < 2:
				continue
			prop_name = prop_parts[0].strip()
			prop_type = prop_parts[1].strip()
			if len(prop_parts) == 3:
				prop_type = join_func_type_or_return_default(prop_parts).strip()
			if prop_name and prop_type:
				props_documented = f" * @prop {{{prop_type}}} {prop_name.replace('?', '')} - \n"
				annotation_lines.append(props_documented)
	return "".join(annotation_lines)


def annotate_type(content: str) -> str:
	ts_types = re.findall(type_pattern, content)

	for whole_ts_type in ts_types:
		type_name = re.search(type_name_pattern, whole_ts_type)
		type_intersections = re.findall(type_intersect_pattern, whole_ts_type)
		type_props = re.findall(type_props_pattern, whole_ts_type)

		if len(type_props) > 0:
			annotation_text = "/**\n"
			annotation_text += annotate_type_props(type_props)
			annotation_text += add_annot_intersection_types(type_intersections)
			annotation_text += " */\n"

			if type_name:
				type_declaration = f"{'export type' if 'export type' in content else 'type'} {type_name.group()}"
				content = content.replace(type_declaration + " =", annotation_text + type_declaration + " =")

	return content


def parse_file(file_path: str) -> str:
	try:
		with open(file_path, 'r') as file:
			return file.read()
	except FileNotFoundError:
		print(f"Ошибка: Файл '{file_path}' не найден.")
	except Exception as e:
		print(f"Произошла ошибка при обработке файла '{file_path}': {str(e)}")


def handle_finish(content, file_path, same_flag = False):
	if same_flag:
		with open(file_path, 'w') as annotated_file:
			annotated_file.write(content)

		print(f"Аннотированный файл сохранен как: {file_path}")
	else:
		annotated_file_path = ""

		if file_path.endswith(".tsx"):
			annotated_file_path = file_path.replace(".tsx", "_annotated.tsx")
		elif file_path.endswith(".ts"):
			annotated_file_path = file_path.replace(".ts", "_annotated.ts")

		with open(annotated_file_path, 'w') as annotated_file:
			annotated_file.write(content)

		print(f"Аннотированный файл сохранен как: {annotated_file_path}")


def process_file(file_path, same_flag = False):
	try:
		content = parse_file(file_path)
		if content is not None:
			was_documented = detect_if_was_documented(pristine, content)
			if was_documented:
				raise Exception(f"Файл {file_path} уже был задокументирован. Пропускаю.")
			else:
				handle_finish(
					annotate_class(
						annotate_type(
							annotate_component(
								content
							))), file_path, same_flag)
	except Exception as e:
		print(f"Произошла ошибка при обработке файла '{file_path}': {str(e)}")


def process_directory(directory_path, same_flag = False):
	for root, dirs, files in os.walk(directory_path):
		for file in files:
			file_path = os.path.join(root, file)
			if file_path.endswith((".tsx", ".ts")):
				process_file(file_path, same_flag)


parser = argparse.ArgumentParser(
	description='Аннотирование файлов TSX/TS.')
parser.add_argument('-s', '--same', action='store_true', help='Аннотировать файлы в исходных местоположениях.')
parser.add_argument('-p', '--pristine', action="store_true", help='Аннотировать только неаннотированые файлы')
parser.add_argument('path', help='Путь к директории или файлу TSX/TS.')

args = parser.parse_args()
path = args.path
same_flag = args.same
pristine = args.pristine

print(same_flag, args.same, args)

if os.path.isdir(path):
	process_directory(path, same_flag)
elif os.path.isfile(path):
	process_file(path, same_flag)
else:
	print(
		f"Указанный путь '{path}' не является директорией или файлом TSX/TS.")

# TODO: детектить не весь документ. а документы отд. методов
