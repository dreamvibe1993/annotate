# 1.7.0

import re
import os
import argparse
from typing import Dict, Union, Callable

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

class_method_pattern = r"\w+\s?\w+.*\([^}]*\):[^=\n]*?{"
class_method_name_pattern = r"\w+(?=\()"
method_params_pattern = r"(?<=\()[^};]+?(?=\):)"
method_param_type_pattern = r"(?<=:\s).+"
method_param_name_pattern = r"[\w?]+(?=:)"

func_type_param_pattern = r'\w+:\s\([^/]*?\)\s=>\s[\w<>\[\]]+\n?'

function_pattern = r"function\s\w+[<\w\s>,&|()=:]*\([^}]*\):[^=\n]*?{"
lambda_pattern = r"const\s\w+\s=\s\([^/]*\).+\s=>\s{"

modifiers = ['get', 'set', 'async', 'private', 'protected', 'abstract']
delimiter: str = "%%%%"
delimiter_letters: str = "ФФФФ"
unrepairable: str = 'unrepairable'
method = "method"
ts_type = "ts_type"
function = "function"

say = print

DEBUG_MODE = True


def log(self, *a):
    if DEBUG_MODE:
        print(self, *a, sep=' ', end='\n', file=None)


def we_have_name_and_type(param_name: "list[str]" or None, param_type: "list[str]" or None) -> bool: return len(
    param_type) > 0 and len(param_name) > 0


def get_type_and_name(pat: Dict[str, str], string_from: str) -> Union[str or None, str or None, bool]:
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


def fmt(s: str) -> str:
    return re.sub(r"[\s\n\t]*?", "", s)


def find_vertical_annotation(string_to_search_for: str, string_to_search_in: str,
                             search_for: ts_type or method) -> str or None:
    possible_only_name = re.search(r"\b\w+\b\(", string_to_search_for, flags=re.MULTILINE)
    only_name = possible_only_name.group(0).replace("(", "") if possible_only_name else string_to_search_for
    annotations = re.findall(r'^\s*$\n\s+/\*\*\n[^%]+?\*/\n\s+',
                             string_to_search_in,
                             flags=re.MULTILINE) if search_for == method else re.findall(
        r'/\*\*\n[^%]+?\*/\n',
        string_to_search_in,
        flags=re.MULTILINE)
    found: str or None = None
    for a in annotations:
        if len(a) == 0: continue
        if search_for == ts_type:
            a += "export type "
        if a + only_name in string_to_search_in:
            if search_for == ts_type:
                a = a.replace('export type ', "")

            found = a
            break
    return found


def find_horiz_annotation(string_to_search_for: str, string_to_search_in: str,
                          search_for: ts_type or method) -> str or None:
    possible_only_name = re.search(r"\b\w+\b\(", string_to_search_for, flags=re.MULTILINE)
    only_name = possible_only_name.group(0).replace("(", "") if possible_only_name else string_to_search_for
    annotations = re.findall(r'/\*\*\s.+\*/\n\s+',
                             string_to_search_in,
                             flags=re.MULTILINE)
    found: str or None = None
    for a in annotations:
        if len(a) == 0: continue
        if search_for == ts_type:
            a += "export type "
        if a + only_name in string_to_search_in:
            found = a
            break
    return found


def find_annotation(string_to_search_for: str, string_to_search_in: str, entity: ts_type or method) -> str or None:
    found: str or None = find_vertical_annotation(string_to_search_for, string_to_search_in,
                                                  entity) or find_horiz_annotation(
        string_to_search_for, string_to_search_in, entity)
    return found


def repair_annotation(annotation: str) -> str:
    param_line = re.search(r"@.+", annotation)
    has_no_types = param_line and not bool(re.search(r"[{}]", param_line.group(0)))
    if has_no_types:
        return unrepairable
    else:
        return annotation


def find_annotation_description(string_to_search_in: str or None) -> str or None:
    if not string_to_search_in: return None
    string_to_search_in = re.sub(r"(?<=\s\*\s)@\w+\s.+$", "", string_to_search_in, flags=re.DOTALL)
    possible_method_description = re.search(r"(?<=\s\*\s)[^@{}]+\n", string_to_search_in,
                                            flags=re.MULTILINE | re.DOTALL)
    if not possible_method_description:
        possible_method_description = re.search(r"(?<=\s)[^@{}]+(?=\*/)", string_to_search_in,
                                                flags=re.MULTILINE | re.DOTALL)
    found = re.sub(r"[/*]", "",
                   possible_method_description.group(0).strip()).strip() if possible_method_description else None
    found = re.sub(r"\s{2,}", "\n", found) if possible_method_description else None
    return found


def replace_modifier_space_with_delim(method, ts_class) -> Union[str, str]:
    modifier_word = ""
    for modifier in modifiers:
        if modifier + " " in method:
            modifier_word = modifier
    meth = method.replace(f'{modifier_word} ', f"{modifier_word}{delimiter_letters}") if modifier_word else method
    klass = ts_class.replace(method, method.replace(f'{modifier_word} ',
                                                    f"{modifier_word}{delimiter_letters}")) if modifier_word else ts_class
    return [meth, klass]


def replace_delim(method, ts_class) -> Union[str, str]:
    meth = method
    klass = ts_class
    for modifier in modifiers:
        modifier_word_with_delim = modifier + delimiter_letters
        if modifier_word_with_delim in method:
            klass = ts_class.replace(method, method.replace(modifier_word_with_delim, modifier + " "))
            meth = method.replace(modifier_word_with_delim, modifier + " ")
    return [meth, klass]



def annotate_functions(entity: str, content: str, typeof_entity: function or method or type) -> str:
    old_annotation: str or None = find_annotation(entity, content, method)
    possible_method_description: str or None = find_annotation_description(old_annotation)
    method_description = possible_method_description or "Описание метода"
    method_params = re.findall(method_params_pattern, entity)
    annotated_method_params = annotate_params(method_params)
    new_annotation = f"/**\n     * {method_description}\n{annotated_method_params}     */\n"
    new_annotation = update_annotation(old_annotation, new_annotation)
    return new_annotation


def annotate_class(content: str) -> str:
    ts_classes: list[str] = re.findall(ts_class_pattern, content)
    for ts_class in ts_classes:
        if not bool(re.search(fr"/\*\*.+\*/\n{re.escape(ts_class)}", content, flags=re.DOTALL)):
            content = content.replace(ts_class, "/** Описание класса */\n" + ts_class)
        class_constructor = re.search(class_constructor_pattern, ts_class)
        if class_constructor:
            if not find_annotation("constructor", ts_class, method):
                constructor = class_constructor.group(0)
                class_constructor_params = re.findall(
                    class_constructor_params_pattern, constructor)
                if len(class_constructor_params) > 0:
                    constructor_annot_text = f'    /**\n{annotate_params(class_constructor_params)}     */\n'
                    content = content.replace(
                        constructor, constructor_annot_text + constructor)
        class_methods: list[str] = re.findall(class_method_pattern, ts_class)
        for class_method in class_methods:
            delimited_modified_entities = replace_modifier_space_with_delim(class_method, content)
            class_method = delimited_modified_entities[0]
            content = delimited_modified_entities[1]
            old_annotation: str or None = find_annotation(class_method, content, method)
            if old_annotation: content = content.replace(old_annotation, "")
            possible_method_description: str or None = find_annotation_description(old_annotation)
            method_description = possible_method_description or "Описание метода"
            method_params = re.findall(method_params_pattern, class_method)
            annotated_method_params = annotate_params(method_params)
            new_annotation = f"/**\n     * {method_description}\n{annotated_method_params}     */\n"
            new_annotation = update_annotation(old_annotation, new_annotation)
            original_modified_entities = replace_delim(class_method, content)
            class_method = original_modified_entities[0]
            content = original_modified_entities[1]
            content = content.replace(class_method, "\n   \t" + new_annotation + "    " + class_method)
    return content


def annotate_functions_and_lambdas(content: str) -> str:
    lambdas: list[str] = re.findall(lambda_pattern, content)
    functions: list[str] = re.findall(function_pattern, content)
    lambdas_and_functions: list[str] = lambdas + functions
    for entity in lambdas_and_functions:
        replacement_candidate: str = f"export {entity}" if f"export {entity}" in content else entity
        old_annotation: str or None = find_annotation(replacement_candidate, content, method)

        possible_method_description: str or None = find_annotation_description(old_annotation)
        method_description = possible_method_description or "Описание функции"
        method_params = re.findall(method_params_pattern, entity)
        annotated_method_params = annotate_params(method_params)
        new_annotation = f"/**\n     * {method_description}\n{annotated_method_params}     */\n"
        if old_annotation: content = content.replace(old_annotation, "")
        new_annotation = update_annotation(old_annotation, new_annotation)
        content = content.replace(replacement_candidate, "\n   \t" + new_annotation + "    " + replacement_candidate)
    return content


def annotate_component(content: str) -> str:
    components: list[str] = re.findall(component_pattern, content)
    for component in components:
        if fmt("*/" + component) in fmt(content): continue
        component_name_found = re.search(
            component_name_pattern, str(component)).group()
        component_with_description: str = f"/**\n * Описание компонента\n"
        if re.search(fr"\b{component_name_found}Props", content):
            component_with_description += f" * @param props {{@link {component_name_found}Props}}\n */\n{component}"
        else:
            component_with_description += f" */\n{component}"
        content = content.replace(component, component_with_description)
    return content


def add_annot_intersection_types(intersections: "list[str]") -> str:
    text = ''
    for intersection in intersections:
        link = f"@link {intersection.strip()}"
        text += f" * @see {{{link}}} \n"
    return text


def annotate_type_props(props: "list[str]") -> str:
    annotation_lines = []
    for prop in list(filter(lambda p: len(p) > 0, props)):
        is_functional_type = "(" in prop and ")" in prop and "=>" in prop
        prop_parts = prop.split(": ") if not is_functional_type else prop.split(": (")
        prop_name = prop_parts[0]
        prop_type = "(" + prop_parts[1] if is_functional_type else prop_parts[1]
        annotation = f" * @prop {{{prop_type}}} {prop_name.replace('?', '')} -\n"
        annotation_lines.append(annotation)
    return "".join(annotation_lines)


def update_annotation(old_annotation: str, new_annotation: str) -> str:
    if not old_annotation: return new_annotation
    old_annotation_formatted = fmt(old_annotation)
    new_annotation_formatted = fmt(new_annotation)
    annotations_are_same = old_annotation_formatted == new_annotation_formatted
    if not annotations_are_same:
        for old_annotation_line in re.findall(r"@.+", old_annotation):
            is_unrepairable = repair_annotation(old_annotation_line) == unrepairable
            if not is_unrepairable:
                continue
            possible_param_name = re.search(r"(?<=\s)\b[a-zA-Z]+\b", old_annotation_line)
            if not possible_param_name:
                continue
            param_to_replace_to_old_one = possible_param_name.group(0)
            line_to_replace_to_old_one = old_annotation_line
            if param_to_replace_to_old_one and line_to_replace_to_old_one:
                new_annotation = re.sub(fr'.+{param_to_replace_to_old_one}.*',
                                        f"* {line_to_replace_to_old_one}",
                                        new_annotation)
        for new_annotation_line in re.findall(r"@.+", new_annotation):
            match = re.search(fr"{re.escape(new_annotation_line)}.+", old_annotation)
            if match:
                new_annotation = new_annotation.replace(new_annotation_line, match.group(0))
    return new_annotation


def annotate_type(content: str) -> str:
    ts_types = re.findall(r"type\s\w+\s=\s.*?};", content, flags=re.DOTALL)
    for whole_ts_type in ts_types:
        type_name = re.search(type_name_pattern, whole_ts_type)
        if not type_name: continue
        type_declaration = f"{'export type' if f'export type {type_name.group(0)}' in content else 'type'} {type_name.group(0)}"
        old_annotation = find_annotation(type_name.group(0), content, ts_type)
        type_intersections = re.findall(type_intersect_pattern, whole_ts_type)
        possible_type_props = re.search(r"{([^}]*)}", whole_ts_type)
        if not possible_type_props: continue
        type_props = list(
            map(lambda prop: prop.strip(), re.sub(r"[{};]", "", possible_type_props.group(0)).split("\n")))
        possible_annotation_description = find_annotation_description(old_annotation)
        annotation_description = "".join(list(map(lambda d: f" * {d}\n", possible_annotation_description.split(
            "\n")))) if possible_annotation_description else ""
        new_annotation = "/**\n"
        new_annotation += annotation_description
        new_annotation += annotate_type_props(type_props)
        new_annotation += add_annot_intersection_types(type_intersections)
        new_annotation += " */\n"
        if old_annotation: content = content.replace(old_annotation, "")
        new_annotation = update_annotation(old_annotation, new_annotation)
        content = content.replace(type_declaration.strip(), new_annotation + type_declaration)
    return content


def parse_file(file_path: str) -> str:
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        say(f"Ошибка: Файл '{file_path}' не найден.")
    except Exception as e:
        say(f"Произошла ошибка при обработке файла '{file_path}': {str(e)}")


def handle_finish(content, file_path, same_flag=False):
    if same_flag:
        with open(file_path, 'w') as annotated_file:
            annotated_file.write(content)

        say(f"Аннотированный файл сохранен как: {file_path}")
    else:
        annotated_file_path = ""

        if file_path.endswith(".tsx"):
            annotated_file_path = file_path.replace(".tsx", "_annotated.tsx")
        elif file_path.endswith(".ts"):
            annotated_file_path = file_path.replace(".ts", "_annotated.ts")

        with open(annotated_file_path, 'w') as annotated_file:
            annotated_file.write(content)

        say(f"Аннотированный файл сохранен как: {annotated_file_path}")


def annotate(content) -> str:
    annotated = annotate_class(
        annotate_type(
            annotate_functions_and_lambdas(
                annotate_component(
                    content
                )
            )
        )
    )
    return annotated


def process_file(file_path, same_flag=False):
    try:
        content = parse_file(file_path)
        if content is not None:
            handle_finish(annotate(content), file_path, same_flag)
    except Exception as e:
        say(f"Произошла ошибка при обработке файла '{file_path}': {str(e)}")


def process_directory(directory_path, same_flag=False):
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.endswith((".tsx", ".ts")):
                process_file(file_path, same_flag)


parser = argparse.ArgumentParser(
    description='Аннотирование файлов TSX/TS.')
parser.add_argument('-s', '--same', action='store_true', help='Аннотировать файлы в исходных местоположениях.')
parser.add_argument('path', help='Путь к директории или файлу TSX/TS.')

args = parser.parse_args()
path = args.path
same_flag = args.same

if os.path.isdir(path):
    process_directory(path, same_flag)
elif os.path.isfile(path):
    process_file(path, same_flag)
else:
    say(
        f"Указанный путь '{path}' не является директорией или файлом TSX/TS.")

# TODO: enums
# TODO: generics в типах
# TODO: сохранять форматирование?
# TODO: interfaces
