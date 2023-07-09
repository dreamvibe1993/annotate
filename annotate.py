# 1.10.1

import re
import os
import argparse
from typing import Dict, Union, Tuple

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

METHOD = "method"
TS_TYPE = "ts_type"
FUNCTION = "function"
LAMBDA = "lambda"
CONSTRUCTOR = 'constructor'

export_type = "export type"

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


def get_parameter_injected(param_type: str, param_name: str, indentation: str) -> str:
    return f"{indentation} * @param {{{param_type}}} {param_name} -\n"


def annotate_params(method_params: "list[str]", indentation: str) -> str:
    params_text = ""
    for line_of_methods_params in method_params:
        for func_type in re.findall(func_type_param_pattern, line_of_methods_params):
            parameter_of_func_type = re.sub(r":\s\(", delimiter + "(", func_type)
            func_param_name = parameter_of_func_type.split(delimiter)[0]
            func_param_type = parameter_of_func_type.split(delimiter)[1]
            params_text += get_parameter_injected(func_param_type, func_param_name, indentation)
            line_of_methods_params = line_of_methods_params.replace(func_type, "")
        if "," not in line_of_methods_params:
            type_of_param, name_of_param, name_and_type_found = get_type_and_name({
                "name": method_param_name_pattern,
                "type": method_param_type_pattern
            }, line_of_methods_params)
            if not name_and_type_found: continue
            params_text += get_parameter_injected(type_of_param, name_of_param, indentation)
            continue
        for param in line_of_methods_params.split(","):
            type_of_param, name_of_param, name_and_type_found = get_type_and_name({
                "name": method_param_name_pattern,
                "type": method_param_type_pattern
            }, param)
            if not name_and_type_found: continue
            for generic in re.findall(r'<.+>', line_of_methods_params):
                type_without_generics = re.sub(r"<\w+>?", "", type_of_param)
                if type_without_generics + generic not in line_of_methods_params: continue
                type_of_param = type_without_generics + generic
            params_text += get_parameter_injected(type_of_param, name_of_param, indentation)

    return params_text


def fmt(s: str) -> str:
    return re.sub(r"[\s\n\t]*?", "", s)


def find_vertical_annotation(target_string: str, source_string: str, search_for: TS_TYPE or METHOD) -> str or None:
    source_string_formatted = source_string.replace(" ", "")
    possible_strictly_name = re.search(r"\b\w+\b\(", target_string, flags=re.MULTILINE)
    strictly_name = target_string
    if possible_strictly_name: strictly_name = possible_strictly_name.group(0).replace("(", "")
    if search_for == METHOD:
        annotations = re.findall(r'\s*?$\n?\s*?/\*\*\n[^%]+?\*/\n\s*', source_string, flags=re.MULTILINE)
    else:
        annotations = re.findall(r'/\*\*\n[^%]+?\*/\n', source_string, flags=re.MULTILINE)
    found: str or None = None
    for annotation in annotations:
        if len(annotation) == 0: continue
        if search_for == TS_TYPE: annotation += f"{export_type} "
        if (annotation + strictly_name).replace(" ", "") not in source_string_formatted: continue
        found = annotation
        break
    if search_for == TS_TYPE and found: found = found.replace(f"{export_type} ", "")
    return found


def find_horizontal_annotation(target_string: str, source_string: str, search_for: TS_TYPE) -> str or None:
    source_string_formatted = source_string.replace(" ", "")
    possible_only_name = re.search(r"\b\w+\b\(", target_string, flags=re.MULTILINE)
    only_name = target_string
    if possible_only_name: only_name = possible_only_name.group(0).replace("(", "")
    annotations = re.findall(r'/\*\*\s.+\*/\n\s+', source_string, flags=re.MULTILINE)
    found: str or None = None
    for annotation in annotations:
        if len(annotation) == 0: continue
        if search_for == TS_TYPE: annotation += f"{export_type} "
        if (annotation + only_name).replace(" ", "") not in source_string_formatted: continue
        found = annotation
        break
    if search_for == TS_TYPE and found: found = found.replace(f"{export_type} ", "")
    return found


def find_annotation(target_string: str, source_string: str, search_for: TS_TYPE or METHOD) -> str or None:
    possible_annotation: str or None = find_vertical_annotation(target_string, source_string, search_for)
    if not possible_annotation: possible_annotation = find_horizontal_annotation(target_string, source_string,
                                                                                 search_for)
    if possible_annotation: possible_annotation = re.sub(r"^$", "", possible_annotation.strip())
    return possible_annotation


def repair_annotation(annotation: str) -> str:
    param_line = re.search(r"@.+", annotation)
    has_no_types = param_line and not bool(re.search(r"[{}]", param_line.group(0)))
    if has_no_types:
        return unrepairable
    else:
        return annotation


def find_annotation_description(source_string: str or None) -> str or None:
    if not source_string: return None
    source_string = re.sub(r"(?<=\s\*\s)@\w+\s.+$", "", source_string, flags=re.DOTALL)
    possible_method_description = re.search(r"(?<=\s\*\s)[^@{}]+\n", source_string,
                                            flags=re.MULTILINE | re.DOTALL)
    if not possible_method_description:
        possible_method_description = re.search(r"(?<=\s)[^@{}]+(?=\*/)", source_string,
                                                flags=re.MULTILINE | re.DOTALL)
    if not possible_method_description: return None
    found = re.sub(r"[/*]", "", possible_method_description.group(0))
    found = re.sub(r"\s{2,}", "\n", found.strip())
    return found


def replace_modifier_space_with_delimiter(entity: str, content: str) -> Tuple[str, str]:
    modifier_word = ""
    for modifier in modifiers:
        if not modifier + " " in entity: continue
        modifier_word = modifier
    if not modifier_word: return [entity, content]
    entity_with_delimiter = entity.replace(f'{modifier_word} ', f"{modifier_word}{delimiter_letters}")
    content_with_delimiter: str = content.replace(entity, entity_with_delimiter)
    return entity_with_delimiter, content_with_delimiter


def replace_delimiter(entity_with_delimiter: str, content_with_delimiter: str) -> Tuple[str, str]:
    entity = entity_with_delimiter
    content = content_with_delimiter
    for modifier in modifiers:
        modifier_word_with_delimiter = modifier + delimiter_letters
        if modifier_word_with_delimiter not in entity_with_delimiter: continue
        entity_without_delimiter = entity.replace(modifier_word_with_delimiter, modifier + " ")
        entity = entity_with_delimiter.replace(entity_with_delimiter, entity_without_delimiter)
        content = content_with_delimiter.replace(modifier_word_with_delimiter, modifier + " ")
    return entity, content


def create_annotation(entity: str, content: str, typeof_entity: FUNCTION or METHOD or TS_TYPE or LAMBDA) -> str:
    delimited_modified_entities = replace_modifier_space_with_delimiter(entity, content)
    entity = delimited_modified_entities[0]
    content = delimited_modified_entities[1]
    possible_indentation = re.search(rf"\s+?(?={re.escape(entity)})", content)
    indentation = re.sub(r"\n", "", possible_indentation.group(0)) if possible_indentation else ""
    old_annotation: str or None = find_annotation(entity, content, typeof_entity)
    if old_annotation: content = content.replace(indentation + old_annotation, "")
    possible_method_description: str or None = find_annotation_description(old_annotation)
    method_description = possible_method_description or ""
    if not possible_method_description:
        if typeof_entity == METHOD:
            method_description = "Описание метода"
        if typeof_entity == FUNCTION or typeof_entity == LAMBDA:
            method_description = "Описание функции"
    method_params = re.findall(method_params_pattern, entity)
    annotated_method_params = annotate_params(method_params, indentation)
    new_annotation = f"\n{indentation}/**\n{indentation} * {method_description}\n{annotated_method_params}{indentation} */\n"
    if indentation: new_annotation = re.sub(fr"({indentation})+", indentation, new_annotation)
    new_annotation = update_annotation(old_annotation, new_annotation, indentation)
    original_modified_entities = replace_delimiter(entity, content)
    entity = original_modified_entities[0]
    content = original_modified_entities[1]
    if typeof_entity == FUNCTION:
        new_entity = indentation + new_annotation + indentation + entity
        content = content.replace(entity, new_entity)
        content = re.sub(rf"(\n{re.escape(indentation)}+\n?)+{re.escape(new_entity)}", "\n" + new_entity, content)
    if typeof_entity == METHOD:
        b_entity = entity
        new_entity = re.sub(r"^(\s)*$\n?", "", new_annotation + indentation + b_entity)
        content = content.replace(entity, new_entity)
        content = re.sub(rf"(\n*{re.escape(indentation)})+\n*{re.escape(new_entity)}", "\n"+new_entity, content)
    if typeof_entity == TS_TYPE:
        new_entity = new_annotation + entity
        content = re.sub(rf"\n?{re.escape(new_entity)}", new_entity, content, flags=re.MULTILINE)
    return content


def annotate_class(content: str) -> str:
    ts_classes: list[str] = re.findall(ts_class_pattern, content)
    for ts_class in ts_classes:
        if not bool(re.search(fr"/\*\*.+\*/\n{re.escape(ts_class)}", content, flags=re.DOTALL)):
            content = content.replace(ts_class, "/** Описание класса */\n" + ts_class)
        class_constructor = re.search(class_constructor_pattern, ts_class)
        if class_constructor and not find_annotation(f"{CONSTRUCTOR}", ts_class, METHOD):
            constructor = class_constructor.group(0)
            class_constructor_params = re.findall(class_constructor_params_pattern, constructor)
            if len(class_constructor_params) < 1: continue
            possible_indentation = re.search(rf"\s*(?={CONSTRUCTOR})", content)
            indentation = possible_indentation.group(0) if possible_indentation else ""
            constructor_annot_text = f"\n{indentation}/**\n{indentation}\n{annotate_params(class_constructor_params, indentation)}{indentation}*/\n"
            content = content.replace(constructor, re.sub(r"^[\s\n]*$\n?", "", constructor_annot_text + constructor, flags=re.MULTILINE))
        class_methods: list[str] = re.findall(class_method_pattern, ts_class)
        for class_method in class_methods: content = create_annotation(class_method, content, METHOD)
    return content


def annotate_functions_and_lambdas(content: str) -> str:
    lambdas: list[str] = re.findall(r"const\s\w+\s=\s\([^/]*?\).+?\s=>\s{", content)
    functions: list[str] = re.findall(function_pattern, content)
    lambdas_and_functions: list[str] = lambdas + functions
    for entity in lambdas_and_functions:
        replacement_candidate: str = f"export {entity}" if f"export {entity}" in content else entity
        content = create_annotation(replacement_candidate, content, FUNCTION)
    return content


def annotate_component(content: str) -> str:
    components: list[str] = re.findall(component_pattern, content)
    for component in components:
        if fmt("*/" + component) in fmt(content): continue
        component_name_found = re.search(component_name_pattern, str(component)).group()
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


def update_annotation(old_annotation: str, new_annotation: str, identation: str) -> str:
    if not old_annotation: return new_annotation
    old_annotation_formatted = fmt(old_annotation)
    new_annotation_formatted = fmt(new_annotation)
    annotations_are_same = old_annotation_formatted == new_annotation_formatted
    if annotations_are_same: return new_annotation
    for old_annotation_line in re.findall(r"@.+", old_annotation):
        is_unrepairable = repair_annotation(old_annotation_line) == unrepairable
        if not is_unrepairable: continue
        possible_param_name = re.search(r"(?<=\s)\b[a-zA-Z]+\b", old_annotation_line)
        if not possible_param_name: continue
        param_to_replace_to_old_one = possible_param_name.group(0)
        line_to_replace_to_old_one = old_annotation_line
        if not param_to_replace_to_old_one or not line_to_replace_to_old_one: continue
        new_annotation = re.sub(fr'.+{param_to_replace_to_old_one}.*', f"{identation} * {line_to_replace_to_old_one}",
                                new_annotation)
    for new_annotation_line in re.findall(r"@.+", new_annotation):
        match = re.search(fr"{re.escape(new_annotation_line)}.+", old_annotation)
        if not match: continue
        new_annotation = new_annotation.replace(new_annotation_line, match.group(0))
    return new_annotation


def annotate_type(content: str) -> str:
    ts_types = re.findall(r"type\s\w+\s=\s.*?};", content, flags=re.DOTALL)
    for whole_ts_type in ts_types:
        possible_type_name = re.search(type_name_pattern, whole_ts_type)
        if not possible_type_name: continue
        type_name = possible_type_name.group(0)
        type_declaration = f"{export_type if f'{export_type} {type_name}' in content else 'type'} {type_name}"
        possible_indentation = re.search(rf"\s*(?={type_declaration})", content)
        indentation = possible_indentation.group(0) if possible_indentation else ""
        old_annotation = find_annotation(possible_type_name.group(0), content, TS_TYPE)
        type_intersections = re.findall(type_intersect_pattern, whole_ts_type)
        possible_type_props = re.search(r"{([^}]*)}", whole_ts_type)
        if not possible_type_props: continue
        type_props = list(
            map(lambda prop: prop.strip(), re.sub(r"[{};]", "", possible_type_props.group(0)).split("\n")))
        possible_annotation_description = find_annotation_description(old_annotation)
        annotation_description = "".join(
            list(map(lambda d: f"{indentation} * {d}\n", possible_annotation_description.split(
                "\n")))) if possible_annotation_description else ""
        new_annotation = "/**\n"
        new_annotation += annotation_description
        new_annotation += annotate_type_props(type_props)
        new_annotation += add_annot_intersection_types(type_intersections)
        new_annotation += " */\n"
        if old_annotation: content = content.replace(old_annotation, "")
        new_annotation = update_annotation(old_annotation, new_annotation, indentation)
        new_entity = new_annotation + type_declaration
        content = content.replace(type_declaration.strip(), new_entity)
        content = re.sub(rf"\n+{re.escape(new_entity)}", "\n\n" + new_entity, content, flags=re.MULTILINE)
    return content


def parse_file(file_path: str) -> str:
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        say(f"Ошибка: Файл '{file_path}' не найден.")
    except Exception as e:
        say(f"Произошла ошибка при обработке файла '{file_path}': {str(e)}")


def handle_finish(content, file_path, should_annotate_same_file=False):
    if should_annotate_same_file:
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


def process_file(file_path, should_annotate_same_file=False):
    try:
        content = parse_file(file_path)
        if content is None: return say("Этот файл пуст!")
        handle_finish(annotate(content), file_path, should_annotate_same_file)
    except Exception as e:
        say(f"Произошла ошибка при обработке файла '{file_path}': {str(e)}")


def process_directory(directory_path, should_annotate_same_file=False):
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            if not file_path.endswith((".tsx", ".ts")): return say(
                "Я умею работать только с файлами формата tsx или ts!")
            process_file(file_path, should_annotate_same_file)


parser = argparse.ArgumentParser(description='Аннотирование файлов TSX/TS.')
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
    say(f"Указанный путь '{path}' не является директорией или файлом TSX/TS.")

# TODO: enums
# TODO: generics в типа
# TODO: interfaces
