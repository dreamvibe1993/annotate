# 1.12.2
# https://github.com/dreamvibe1993/annotate

import re
import os
import argparse
from typing import Dict, Union, Tuple

method_param_type_pattern = r"(?<=:\s).*"
method_param_name_pattern = r"[\w?]+(?=:)"

modifiers = ['get', 'set', 'async', 'private', 'protected', 'abstract']
delimiter_letters: str = "ФФФФ"
unrepairable: str = 'unrepairable'

METHOD = "method"
TS_TYPE = "ts_type"
FUNCTION = "function"
LAMBDA = "lambda"
CONSTRUCTOR = 'constructor'

export_type = "export type"

say = print


def get_type_and_name(pat: Dict[str, str], string_from: str) -> Union[str or None, str or None, bool]:
    param_type = re.findall(pat["type"], string_from, flags=re.DOTALL)
    param_name = re.findall(pat["name"], string_from)
    if len(param_type) > 0 and len(param_name) > 0:
        return [param_type[0], param_name[0].replace('?', ''), True]
    else:
        return [None, None, False]


def get_parameter_injected(typeof_entity: str, param_type: str, param_name: str, indentation: str) -> str:
    if ignore_types_flag: return f"{indentation} * @{typeof_entity} {param_name} -\n"
    return f"{indentation} * @{typeof_entity} {{{param_type}}} {param_name} -\n"


def annotate_params(method_params: "list[str]", indentation: str) -> str:
    params_text = ""
    for line_of_methods_params in method_params:
        for func_type in re.findall(r'\w+:\s\([^/]*?\)\s=>\s[\w<>\[\]]+\n?', line_of_methods_params):
            parameter_of_func_type = re.sub(r":\s\(", delimiter_letters + "(", func_type)
            func_param_name, func_param_type = parameter_of_func_type.split(delimiter_letters)
            params_text += get_parameter_injected("param", func_param_type, func_param_name, indentation)
            line_of_methods_params = line_of_methods_params.replace(func_type, "")
        if "," not in line_of_methods_params:
            type_of_param, name_of_param, name_and_type_found = get_type_and_name({
                "name": method_param_name_pattern,
                "type": method_param_type_pattern
            }, line_of_methods_params)
            if not name_and_type_found: continue
            params_text += get_parameter_injected("param", type_of_param, name_of_param, indentation)
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
            params_text += get_parameter_injected("param", type_of_param, name_of_param, indentation)
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


def annotate(entity: str, content: str, typeof_entity: FUNCTION or METHOD or TS_TYPE or LAMBDA) -> str:
    entity, content = replace_modifier_space_with_delimiter(entity, content)
    indentation = get_indentation(rf"^ +(?=\w)", entity)
    old_annotation: str or None = find_annotation(entity, content, typeof_entity)
    if old_annotation: content = content.replace(indentation + old_annotation, "")
    possible_method_description: str or None = find_annotation_description(old_annotation)
    method_description = possible_method_description or get_default_description(typeof_entity)
    method_params = re.findall(r"(?<=\()[^};]+?(?=\):)", entity)
    # Эта чепуха нужна, чтобы детектить параметры функций и методов без типов!---------------|
    if len(method_params) < 1: method_params = re.findall(r"(?<=\()[^};]+?(?=\)):?", entity)
    # ---------------------------------------------------------------------------------------|
    annotated_method_params = annotate_params(method_params, indentation)
    new_annotation = f"\n{indentation}/**\n{indentation} * {method_description}\n{annotated_method_params}{indentation} */\n"
    new_annotation = update_annotation(old_annotation, new_annotation, indentation)
    entity, content = replace_delimiter(entity, content)
    return insert_annotation(new_annotation, entity, typeof_entity, indentation, content)


def get_default_description(typeof_entity: FUNCTION or METHOD or LAMBDA) -> str:
    if typeof_entity == METHOD:
        return "Описание метода"
    if typeof_entity == FUNCTION or typeof_entity == LAMBDA:
        return "Описание функции"
    return ""


def get_indentation(regex: str, source_string: str) -> str:
    possible_indentation = re.search(regex, source_string, flags=re.MULTILINE)
    indentation = possible_indentation.group(0) if possible_indentation else ""
    return indentation


def insert_annotation(new_annotation: str, entity: str, typeof_entity: FUNCTION or METHOD or TS_TYPE,
                      indentation: str, content: str) -> str:
    if typeof_entity == TS_TYPE:
        new_entity = new_annotation + entity
        content = re.sub(rf"\n?{re.escape(new_entity)}", new_entity, content, flags=re.MULTILINE)
    if typeof_entity == FUNCTION:
        new_entity = indentation + new_annotation + indentation + entity
        content = content.replace(entity, new_entity)
        content = re.sub(rf"(\n{re.escape(indentation)}+\n?)+{re.escape(new_entity)}", "\n" + new_entity, content)
    if typeof_entity == METHOD:
        new_entity = re.sub(r"^(\s)*$\n?", "", new_annotation + entity)
        new_entity = re.sub(r"^\n*", "", new_entity, flags=re.MULTILINE)
        content = content.replace(entity, new_entity)
    return content


def annotate_class(content: str) -> str:
    ts_classes: list[str] = re.findall(r"export\sclass\s[A-Z]\w+[^{}]*{[^\r]+}", content)
    for ts_class in ts_classes:
        ts_class_no_extra_lines = re.sub(r"^[\s\n]+$", "", ts_class, flags=re.MULTILINE)
        content = content.replace(ts_class, ts_class_no_extra_lines)
        if not bool(re.search(fr"/\*\*.+\*/\n{re.escape(ts_class)}", content, flags=re.DOTALL)):
            content = content.replace(ts_class, "/** Описание класса */\n" + ts_class)
        class_constructor = re.search(r"[^\n]+constructor\([^}]*\)\s{[^}]*}", ts_class)
        if class_constructor and not find_annotation(f"{CONSTRUCTOR}", ts_class, METHOD):
            constructor = class_constructor.group(0)
            class_constructor_params = re.findall(r"(?<=\()[^}]+(?=\)\s)", constructor)
            if len(class_constructor_params) < 1: continue
            indentation = get_indentation(rf"\s*(?={CONSTRUCTOR})", content)
            constructor_annot_text = f"\n{indentation}/**\n{indentation}\n{annotate_params(class_constructor_params, indentation)}{indentation}*/\n"
            content = content.replace(constructor, re.sub(r"^[\s\n]*$\n?", "", constructor_annot_text + constructor,
                                                          flags=re.MULTILINE))
        content = annotate_class_methods(content)
    ts_classes: list[str] = re.findall(r"export\sclass\s[A-Z]\w+[^{}]*{[^\r]+}", content)
    # TODO: Fix this mess vvv
    for ts_class in ts_classes:
        ts_class_no_extra_lines = re.sub(r"^[\s\n]+$", "", ts_class, flags=re.MULTILINE)
        content = content.replace(ts_class, ts_class_no_extra_lines)
        if not bool(re.search(fr"/\*\*.+\*/\n{re.escape(ts_class)}", content, flags=re.DOTALL)):
            content = content.replace(ts_class, "/** Описание класса */\n" + ts_class)
    # ------------------------
    return content


def annotate_class_methods(content: str) -> str:
    class_methods: list[str] = re.findall(r" *?\w+\s?\w+.*\([^}]*\):[^=\n]*?{", content)
    if len(class_methods) < 1:
        class_methods += re.findall(r" *?\w+\s?\w+.*\([^}]*\) *?{", content)
        for method in class_methods:
            if CONSTRUCTOR in method: class_methods.remove(method)
    for class_method in class_methods: content = annotate(class_method, content, METHOD)
    return content


def annotate_functions_and_lambdas(content: str) -> str:
    lambdas: list[str] = re.findall(r"const \w+ = \([^/]*?\).*? => {", content)
    functions: list[str] = re.findall(r"function\s\w+[<\w\s>,&|()=:]*\([^}]*\):?[^=\n]*?{", content)
    lambdas_and_functions: list[str] = lambdas + functions
    for entity in lambdas_and_functions:
        replacement_candidate: str = f"export {entity}" if f"export {entity}" in content else entity
        content = annotate(replacement_candidate, content, FUNCTION)
    return content


def annotate_component(content: str) -> str:
    components: list[str] = re.findall(r"export\s+const\s\w+\s=.+JSX.Element\s=>\s{", content)
    for component in components:
        if fmt("*/" + component) in fmt(content): continue
        component_name_found = re.search(r"(?<=\s)[A-Z]\w+(?=\s=\s)", str(component)).group()
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
        annotation = get_parameter_injected('prop', prop_type, prop_name.replace('?', ''), "")
        annotation_lines.append(annotation)
    return "".join(annotation_lines)


def update_annotation(old_annotation: str, new_annotation: str, indentation: str) -> str:
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
        new_annotation = re.sub(fr'.+{param_to_replace_to_old_one}.*', f"{indentation} * {line_to_replace_to_old_one}",
                                new_annotation)
    for new_annotation_line in re.findall(r"@.+", new_annotation):
        match = re.search(fr"{re.escape(new_annotation_line)}.+", old_annotation)
        if not match: continue
        new_annotation = new_annotation.replace(new_annotation_line, match.group(0))
    return new_annotation


def annotate_type(content: str) -> str:
    ts_types = re.findall(r"type\s\w+\s=\s.*?};", content, flags=re.DOTALL)
    for whole_ts_type in ts_types:
        possible_type_props = re.search(r"{([^}]*)}", whole_ts_type)
        if not possible_type_props: continue
        possible_type_name = re.search(r"(?<=type\s)\w+(?=\s=\s)", whole_ts_type)
        if not possible_type_name: continue
        type_name = possible_type_name.group(0)
        type_declaration = f"{export_type if f'{export_type} {type_name}' in content else 'type'} {type_name}"
        indentation = get_indentation(rf"\s*(?={type_declaration})", content)
        old_annotation = find_annotation(possible_type_name.group(0), content, TS_TYPE)
        if old_annotation: content = content.replace(old_annotation, "")
        type_props_list = re.sub(r"[{};]", "", possible_type_props.group(0)).split("\n")
        type_props_list = list(map(lambda prop: prop.strip(), type_props_list))
        types_props_annotated = annotate_type_props(type_props_list)
        type_intersections = re.findall(r"\w+(?=\s&)", whole_ts_type)
        intersections_annotated = add_annot_intersection_types(type_intersections)
        possible_annotation_description = find_annotation_description(old_annotation)
        annotation_description_list = possible_annotation_description.split(
            "\n") if possible_annotation_description else []
        annotation_description = "".join(list(map(lambda d: f"{indentation} * {d}\n", annotation_description_list)))
        new_annotation = f"/**\n{annotation_description}{types_props_annotated}{intersections_annotated} */\n"
        new_annotation = update_annotation(old_annotation, new_annotation, indentation)
        new_entity = new_annotation + type_declaration
        content = content.replace(type_declaration, new_entity)
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


def run_pipeline(content) -> str:
    return annotate_class(
        annotate_type(
            annotate_functions_and_lambdas(
                annotate_component(
                    content
                )
            )
        )
    )


def process_file(file_path, should_annotate_same_file=False):
    try:
        content = parse_file(file_path)
        if content is None: return say("Этот файл пуст!")
        new_content = run_pipeline(content)
        handle_finish(new_content, file_path, should_annotate_same_file)
    except Exception as e:
        say(f"Произошла ошибка при обработке файла '{file_path}': {str(e)}")


def process_directory(directory_path, should_annotate_same_file=False):
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            if not file_path.endswith((".tsx", ".ts")): return say(
                "Я умею работать только с файлами формата tsx или ts!")
            process_file(file_path, should_annotate_same_file)


def process_user_input(user_input: str) -> str:
    first_line = user_input
    user_input_lines = user_input.splitlines()
    if len(user_input_lines) > 0: first_line = user_input_lines[0]
    if len(first_line.strip()) == 0:
        for line in user_input_lines:
            if len(line) > 1:
                first_line = line
                break
    if "type" in first_line:
        new_content = annotate_type(user_input)
    elif "JSX.Element" in first_line:
        new_content = annotate_component(user_input)
    elif "class" in first_line:
        new_content = annotate_class(user_input)
    elif "function" in first_line:
        new_content = annotate_functions_and_lambdas(user_input)
    elif "const" in first_line and "=>" in first_line:
        new_content = annotate_functions_and_lambdas(user_input)
    else:
        new_content = annotate_class_methods(user_input)
    return new_content


def run_interactive():
    while True:
        lines = []
        say("Введите сущность, документацию к которой вы хотели бы сгенерировать, нажмите Enter и затем Ctrl-D или Ctrl-Z (windows): \n")
        while True:
            try:
                line = input()
            except EOFError:
                break
            lines.append(line)
        user_input = '\n'.join(lines)
        say("\nВы ввели: \n", user_input, "\n")
        new_content = process_user_input(user_input)
        say('\n\n-----НАЧАЛО АННОТАЦИИ-----\n\n')
        say(new_content)
        say('\n\n-----КОНЕЦ  АННОТАЦИИ-----\n\n')
        say('Спасибо!\n')


def main(config: Dict[str, str]):
    interactive = config['interactive']
    same = config['same']
    path = config['path']

    if interactive: run_interactive()

    if not path:
        return say("Недостаточно аргументов! Вызовите скрипт с флагом -h для подсказки.")

    if os.path.isdir(path):
        process_directory(path, same)
    elif os.path.isfile(path):
        process_file(path, same)
    else:
        say(f"Указанный путь '{path}' не является директорией или файлом TSX/TS.")


parser = argparse.ArgumentParser(description='Аннотирование файлов TSX/TS.')
parser.add_argument('-s', '--same', action='store_true', help='Аннотировать файлы в исходных местоположениях.')
parser.add_argument('-T', '--ignore_types', action='store_true', help="Не добавлять типы в аннотацию.")

group = parser.add_mutually_exclusive_group()
group.add_argument('-i', '--interactive', action='store_true',
                   help='Интерактивный режим. Работа с пользовательским вводом.')
group.add_argument('path', nargs="?", help='Путь к директории или файлу TSX/TS.')

args = parser.parse_args()
path_argument = args.path
same_flag = args.same
interactive_flag = args.interactive
ignore_types_flag = args.ignore_types

configuration = {
    "path": path_argument,
    "same": same_flag,
    "interactive": interactive_flag,
    "ignore_types": ignore_types_flag
}

main(configuration)

# TODO: enums
# TODO: generics в типах
# TODO: interfaces
