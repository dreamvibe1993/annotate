import re

from annotate import annotate
from annotate.utils.utils import fmt

class_one = ''' export class TestClassOne {
    constructor() {
    }
    methodOne(): void {
    }
}
'''


def test_annotate_class_one() -> None:
	assert annotate.annotate_class("") == ""
	assert "/** Описание класса */\n" in annotate.annotate_class(class_one)
	assert f"/**\n     * Описание метода\n     */\n" in annotate.annotate_class(class_one)


class_two = ''' export class TestClassTwo {
    constructor(getBatchSelectOptions: GetBatchSelectOptions<T>, entity: string, portionSize: number) {
    }
    methodOne(isFirstLoading: boolean, options: T[]): void {
    }
    methodTwo(formValues: InitialValues, onSuccess?: () => void): Promise<void> {
    }

}
'''


def test_annotate_class_two() -> None:
	class_two_annotated: str = fmt(annotate.annotate_class(class_two))
	assert fmt("/** Описание класса */\n") in class_two_annotated
	assert fmt('''
   /**
     * @param {GetBatchSelectOptions<T>} getBatchSelectOptions -
     * @param {string} entity -
     * @param {number} portionSize -
     */
    constructor(getBatchSelectOptions: GetBatchSelectOptions<T>, entity: string, portionSize: number) {
    }
	''') in class_two_annotated

	assert fmt('''
	/**
	 * Описание метода
	 * @param {InitialValues} formValues -
	 * @param {() => void} onSuccess - 
	 */
	methodTwo(formValues: InitialValues, onSuccess?: () => void): Promise<void> {
	
	}
	''') in class_two_annotated
