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


class_three = ''' export class TestClassTwo {
    constructor(
        accessPermissionRequests: AccessPermissionRequests<Permission, PermissionDTO>,
        getPermissionDTO: GetPermissionDTO<Permission, InitialValues, PermissionDTO>,
    ) {
        makeObservable(this, permissionsModelObservables);
        this.accessPermissionRequests = accessPermissionRequests;
        this.getPermissionDTO = getPermissionDTO;
    }
}
'''


def test_generics_detection_in_constructor() -> None:
	assert fmt('''
		   /**
 * @param {AccessPermissionRequests<Permission, PermissionDTO>} accessPermissionRequests - 
 * @param {GetPermissionDTO<Permission, InitialValues, PermissionDTO>} getPermissionDTO - 
 */
	''') in fmt(annotate.annotate_class(class_three))


class_four = '''
 export class TestClassTwo {
    methodOne(  
        accessPermissionRequests2: AccessPermissionRequests<Permission, PermissionDTO>,
        getPermissionDTO2: GetPermissionDTO<Permission, InitialValues, PermissionDTO>,
		something: string,
		weirdFunction: () => void,
		lolskiy: boolean
        ): void {
        console.log()
    }
}


'''


# constructor(
# 	accessPermissionRequests: AccessPermissionRequests < Permission, PermissionDTO >,
# getPermissionDTO: GetPermissionDTO < Permission, InitialValues, PermissionDTO >,
# ) {
# 	makeObservable(this, permissionsModelObservables);
# this.accessPermissionRequests = accessPermissionRequests;
# this.getPermissionDTO = getPermissionDTO;
# }

def test_generics_detection_in_method() -> None:
	assert fmt('''
		   /**
			 * Описание метода 
			 * @param {AccessPermissionRequests<Permission, PermissionDTO>} accessPermissionRequests2 - 
			 * @param {GetPermissionDTO<Permission, InitialValues, PermissionDTO>} getPermissionDTO2 - 
			 * @param {string} something - 
			 * @param {() => void} weirdFunction - 
			 * @param {boolean} lolskiy - 
			 */
	''') in fmt(annotate.annotate_class(class_four))
