# Annotate

Утилита для генерации jsdoc аннотаций для ts и tsx файлов.

## Использование

```bash
 annotate.py [-h] [-s] [-T] [-i | path]
```
```js
// Результат:

/**
 * Описание метода
 * @param {unknown} event -
 * @param {number} page -
 */
changePage(event: unknown, page: number): void {
    this.page = page;
}
``` 

+ ### Интерактивный режим. Работа с пользовательским вводом.
    ```bash
      python ./annotate.py -i
    ```
+ ### Работа с путем
    ```bash
      python ./annotate.py ~/path_to_ts_or_tsx_file.(tsx|ts)
    ```
+ ### Не добавлять типы в аннотацию.
    ```bash
      python ./annotate.py -T ~/path_to_ts_or_tsx_file.(tsx|ts)
    ```
    ```js
    // Результат:
  
    /**
     * Описание метода
     * @param event -
     * @param page -
     */
    changePage(event: unknown, page: number): void {
        this.page = page;
    }
  ```
+ ### Перезапись файлов в исходном положении
    ```bash
      python ./annotate.py -s ~/path_to_ts_or_tsx_file.(tsx|ts)
    ```
+ ### Помощь
    ```bash
      python ./annotate.py -h
    ```