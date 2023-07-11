# Annotate

Утилита для генераций jsdoc аннотаций для ts и tsx файлов.

## Использование

```bash
 annotate.py [-h] [-s] [-i | path]
```

+ ### Интерактивный режим. Работа с пользовательским вводом.
    ```bash
      python ./annotate.py -i
    ```
+ ### Работа с путем
    ```bash
      python ./annotate.py ~/path_to_ts_or_tsx_file.tsx
    ```
+ ### Перезапись файлов в исходном положении
    ```bash
      python ./annotate.py -s ~/path_to_ts_or_tsx_file.tsx
    ```
+ ### Помощь
    ```bash
      python ./annotate.py -h
    ```