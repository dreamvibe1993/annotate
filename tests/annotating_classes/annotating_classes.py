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
	
	constructor(
	accessPermissionRequests: AccessPermissionRequests <Permission, PermissionDTO>,
getPermissionDTO: GetPermissionDTO <Permission, InitialValues, PermissionDTO>,
) {
	makeObservable(this, permissionsModelObservables);
this.accessPermissionRequests = accessPermissionRequests;
this.getPermissionDTO = getPermissionDTO;
}
	
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


def test_generics_detection_in_method() -> None:
	assert fmt('''
		   /**
			 * Описание метода 
			 * @param {() => void} weirdFunction - 
			 * @param {AccessPermissionRequests<Permission, PermissionDTO>} accessPermissionRequests2 - 
			 * @param {GetPermissionDTO<Permission, InitialValues, PermissionDTO>} getPermissionDTO2 - 
			 * @param {string} something - 
			 * @param {boolean} lolskiy - 
			 */
	''') in fmt(annotate.annotate_class(class_four)) and fmt('''
		   /**
 * @param {AccessPermissionRequests<Permission, PermissionDTO>} accessPermissionRequests - 
 * @param {GetPermissionDTO<Permission, InitialValues, PermissionDTO>} getPermissionDTO - 
 */
	''') in fmt(annotate.annotate_class(class_four))


class_five = '''
 export class TestClassTwo {
	
    methodOne(  
		weirdFunction: (one: number, two: string, three: boolean) => void,
		lolskiy: boolean
        ): void {
        console.log()
    }
}


'''


def test_signatures_of_function_type() -> None:
	assert fmt('''
			   /**
				 * Описание метода 
				 * @param {(one: number, two: string, three: boolean) => void} weirdFunction - 
				 * @param {boolean} lolskiy - 
				 */
		''') in fmt(annotate.annotate_class(class_five))


class_six = '''
export class TestClassTwo {
		
	setSelects(fun: (a: number, b: string, c: PermissionSettingsDTO<Permission>) => Promise<void>): void {
		this.roleConditionOptions = selects.rolesConditions;
	this.lifecycleStatesOptions = selects.lifecycles;
	}
	
	setSelects2(fun: (a: number, b: string, c: PermissionSettingsDTO<Permission>) => string[]): void {
		this.roleConditionOptions = selects.rolesConditions;
	this.lifecycleStatesOptions = selects.lifecycles;
	}
	
	setSelects3(
		fun: (a: number, b: string, c: PermissionSettingsDTO<Permission>) => string[],
		funny: () => VeryVeryLongTypePermissionSettingsDTO
	): void {
		this.roleConditionOptions = selects.rolesConditions;
		this.lifecycleStatesOptions = selects.lifecycles;
	}
	
	setSelects4(
		a: number, 
		b: string, 
		funny: (make: string) => PermissionSettingsDT2O[], 
		c: PermissionSettingsDTO<Permission>
	): void {
        this.roleConditionOptions = selects.rolesConditions;
        this.lifecycleStatesOptions = selects.lifecycles;
    }
    
    setSelects5(a: number, funny: (make: string) => Ppt[], c: PermissionSettingsDTO<Permission>): void {
        this.roleConditionOptions = selects.rolesConditions;
        this.lifecycleStatesOptions = selects.lifecycles;
    }
}
'''


def test_method_promise_void_return_type() -> None:
	assert fmt('''
			     /**
     * Описание метода
     * @param {(a: number, b: string, c: PermissionSettingsDTO<Permission>) => Promise<void>} fun - 
     */ setSelects
		''') in fmt(annotate.annotate_class(class_six))


def test_method_string_array_return_type() -> None:
	assert fmt('''
	  /**
     * Описание метода
     * @param {(a: number, b: string, c: PermissionSettingsDTO<Permission>) => string[]} fun - 
     */ setSelects2
		''') in fmt(annotate.annotate_class(class_six))


def test_method_line_breaking() -> None:
	assert fmt('''
	    /**
     * Описание метода
     * @param {(a: number, b: string, c: PermissionSettingsDTO<Permission>) => string[]} fun -
     * @param {() => VeryVeryLongTypePermissionSettingsDTO} funny -
     */setSelects3
		''') in fmt(annotate.annotate_class(class_six))


def test_method_line_breaking_when_func_between_primitives() -> None:
	assert fmt('''
	     /**
     * Описание метода
     * @param {(make: string) => PermissionSettingsDT2O[]} funny - 
     * @param {number} a - 
     * @param {string} b - 
     * @param {PermissionSettingsDTO<Permission>} c - 
     */setSelects4
		''') in fmt(annotate.annotate_class(class_six))


def test_method_line_breaking_when_func_between_primitives_in_one_line() -> None:
	assert fmt('''
	     /**
     * Описание метода
     * @param {(make: string) => Ppt[]} funny - 
     * @param {number} a - 
     * @param {PermissionSettingsDTO<Permission>} c - 
     */setSelects5
		''') in fmt(annotate.annotate_class(class_six))
