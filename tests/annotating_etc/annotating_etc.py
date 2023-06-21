from annotate import annotate
from annotate.utils.utils import fmt

lambda_one: str = '''

export const useMaxBreadcrumbsItems = (
    containerRef: React.RefObject<HTMLDivElement>,
    itemWidth: number = maxItemWidth,
): number => {
    useEffect(() => {
    }, []);
};


'''

lambda_two: str = '''

export const formatDateAndTime = (intl: IntlShape, date?: Date, defaultMessage = '-'): string => {
    const intlDate = intl.formatDate(date);
    const intlTime = intl.formatTime(date);

    return date ? `${intlDate}, ${intlTime}` : defaultMessage;
};


'''
lambda_three: str = '''

export const doe = (intl: () => void, date?: () => Promise<Testing>, defaultMessage: boolean[]): string => {
    const intlDate = intl.formatDate(date);
    const intlTime = intl.formatTime(date);

    return date ? `${intlDate}, ${intlTime}` : defaultMessage;
};


'''

lambda_four: str = '''

export const fooBazAndQux = (
    intl: () => void,
    date?: () => Promise<Testing>,
    defaultMessage: boolean[],
    defaultFoo: Promise<void>[],
    defaultBaz: string[],
): string => {
    const intlDate = intl.formatDate(date);
    const intlTime = intl.formatTime(date);

    return date ? `${intlDate}, ${intlTime}` : defaultMessage;
};

'''

function_one: str = '''

export function createDropzoneFileInstance(fileDTO: FileDTO): DropzoneFile {
    file.isUploaded = true;
    file.id = id;
    return file;
}


'''

function_two: str = '''

export function getFunky(items: SidebarItem[], selectedItemId: string): string[] {
    file.isUploaded = true;
    file.id = id;
    return file;
}

'''

function_three: str = '''

export function useCoreFeature<FName extends keyof CoreFeatures>(featureName: FName): [boolean, CoreFeatures[FName]] {

    return [!!featureValue, featureValue];
}


'''

function_four: str = '''

export function createServerTitleBreadcrumbs<
    BreadcrumbsLocation extends string = DefaultBreadcrumbsLocation,
    BreadcrumbsEntity extends string = DefaultBreadcrumbsEntity,
>(
    doe: string,
    qux: boolean[],
    funkyFun: (crap: string) => string[],
    mammaMia: MammaMia,
    johnDoe: Person<Woman>,
): UseServerTitleBreadcrumbsHook<BreadcrumbsLocation, BreadcrumbsEntity> {
    return (props) => {
        return [routes, isLoading];
    };
}


'''


def test_annotating_simple_lambda() -> None:
	assert fmt('''
/**
 * Описание функции
 * @param {React.RefObject<HTMLDivElement>} containerRef -
 * @param {number = maxItemWidth} itemWidth -
 */export const useMaxBreadcrumbsItems
	''') in fmt(annotate.annotate_functions_and_lambdas(lambda_one))


def test_annotating_lambda_with_weird_params() -> None:
	assert fmt('''
/**
 * Описание функции
 * @param {IntlShape} intl -
 * @param {Date} date -
 */export const formatDateAndTime
	''') in fmt(annotate.annotate_functions_and_lambdas(lambda_two))


def test_annotating_lambda_with_weirder_params() -> None:
	assert fmt('''
/**
 * Описание функции
 * @param {() => void} intl -
 * @param {() => Promise<Testing>} date -
 * @param {boolean[]} defaultMessage -
 */export const doe
	''') in fmt(annotate.annotate_functions_and_lambdas(lambda_three))


def test_annotating_lambda_with_weird_params_with_linebreaks() -> None:
	assert fmt('''/**
 * Описание функции
 * @param {() => void} intl -
 * @param {() => Promise<Testing>} date -
 * @param {boolean[]} defaultMessage -
 * @param {Promise<void>[]} defaultFoo -
 * @param {string[]} defaultBaz -
 */export const fooBazAndQux
	''') in fmt(annotate.annotate_functions_and_lambdas(lambda_four))


def test_annotating_simple_function() -> None:
	assert fmt('''
	/**
 * Описание функции
 * @param {FileDTO} fileDTO -
 */export function createDropzoneFileInstance
		''') in fmt(annotate.annotate_functions_and_lambdas(function_one))


def test_annotating_trickier_function() -> None:
	assert fmt('''
/**
 * Описание функции
 * @param {SidebarItem[]} items -
 * @param {string} selectedItemId -
 */export function getFunky
		''') in fmt(annotate.annotate_functions_and_lambdas(function_two))


def test_annotating_function_with_generics() -> None:
	assert fmt('''
/**
 * Описание функции
 * @param {FName} featureName -
 */export function useCoreFeature
		''') in fmt(annotate.annotate_functions_and_lambdas(function_three))


def test_annotating_function_with_generics_linebreaks_and_dreadful_args() -> None:
	assert fmt('''
/**
 * Описание функции
 * @param {(crap: string) => string[]} funkyFun -
 * @param {string} doe -
 * @param {boolean[]} qux -
 * @param {MammaMia} mammaMia -
 * @param {Person<Woman>} johnDoe -
 */export function createServerTitleBreadcrumbs
		''') in fmt(annotate.annotate_functions_and_lambdas(function_four))


mixed_one: str = '''

type ConfirmationDialogProps = ModalProps2 &
    Ke2k &
    Lol2 &
    One2 &
    Two2 & {
        onDownload: (file: FileDTO) => Promise<void>;
        onError?: (error: any) => void;
        id: string;
        keepMounted: boolean;
        onConfirm: PromiseVoidFunction;
        title: ReactNode;
        message?: ReactNode;
        confirmText?: string;
        maxWidth?: Breakpoint | false;
    };


export const useLoading = (load: PromiseVoidFunction): JSX.Element | null => {
    const [isLoading, enableLoading, disableLoading] = useFlag(true);

    useEffect((): void => {
        enableLoading();
        load().finally(disableLoading);
    }, [load]);

    return isLoading ? <Loader fullSize /> : null;
};

export const ConfirmationDialog = observer((props: ConfirmationDialogProps): JSX.Element => {
    const intl = useIntl();

    const {
        confirmText = intl.formatMessage({ id: 'common.confirm' }),
        onConfirm,
        onCancel,
        open,
        title,
        message,
        maxWidth = 'xs',
        id,
        ...other
    } = props;

    const [isSubmitting, endIcon, actionHandler] = useAntiDoubleClick(onConfirm);

    const cancelButton: DialogCancelButtonConfig = {
        onClick: onCancel,
    };

    const submitButton: DialogSubmitButtonConfig = {
        onClick: actionHandler,
        disabled: isSubmitting,
        text: confirmText,
        type: 'submit',
        endIcon,
    };

    const titleId = id + '-title';

    return (
        <Dialog fullWidth maxWidth={maxWidth} aria-labelledby={titleId} open={open} {...other}>
            <DialogTitle id={titleId} onCloseClick={onCancel}>
                {title}
            </DialogTitle>
            <DialogContent>{message}</DialogContent>
            <DialogActions cancelButton={cancelButton} submitButton={submitButton} />
        </Dialog>
    );
});


export function useCoreFeature<FName extends keyof CoreFeatures>(featureName: FName): [boolean, CoreFeatures[FName]] {
    const { features }: { features: CoreFeatures } = useCoreStore() as CoreRootStore;
    const featureValue = features[featureName];

    return [!!featureValue, featureValue];
}

export const permissionsModelObservables = {
    accessLolaRequests: observable,
    selectedLolaIndex: observable,

    newLolasDTO: computed,

    load: action.bound,
    accessLolaMapToNewLolaDTO: action.bound,
    setIsLoading: action.bound,
};


export class Bark<
    Foo extends DTO1 = DTO2,
    Guiko extends Mice = Cats,
    Lol extends Novs = Qux,
> {
    accessDaddyRequests: Dream<One, Three>;
    
    lalaPopo: number | null = null;
    yandex = '';
    
    canLoad: Stupefiant[] = [];
    isLoading = true;
    
    serverErrors = new ServerErrorsModel<DefaultAccessDaddyField>();
    getDaddyDTO: GetDaddyDTO<Daddy, InitialValues, DaddyDTO>;

    
    bossBoss: AbcDef[] = [];
    
    lifecycleStatesOptions: Mirtle[] = [];

    constructor(
        accessDaddyRequests: Boss<Daddy, Throw>,
        getDaddyDTO: Bruce<Daddy, InitialValues, Throw>,
    ) {
        makeObservable(this, permissionsModelObservables);
		const letMeDown: Mommy = ['pseudo', "code"]<Uri>;
		let constMeDown: Mommy = ['pseudo', "code"]<Uri>;
        (): void<MegaDooDoo> => {
            	console.log('I am just a test and');
				console.log('I will never be executed :(');
        }()
    }

    
    get newDaddysDTO(): DaddyDTO[] {
		console.log('I am just a test and');
		console.log('I will never be executed :(');
    }

    
    load(): Promise<void> {
    	console.log('I am just a test and');
		console.log('I will never be executed :(');
    }

    
    getGychas(): Promise<void> {
        this.setIsLoading(true);
		console.log('I am just a test and');
		console.log('I will never be executed :(');
    }

    submitGexOrals(formValues: InitialValues, onSuccess?: VoidFunction): Promise<void> {
     		const letMeDown: Mommy = ['pseudo', "code"]<Uri>;
		let constMeDown: Mommy = ['pseudo', "code"]<Uri>;
        (): void<MegaDooDoo> => {
            	console.log('I am just a test and');
				console.log('I will never be executed :(');
        }()
    }

    
    deleteGexOral(): Promise<void> {
   		const letMeDown: Mommy = ['pseudo', "code"]<Uri>;
		let constMeDown: Mommy = ['pseudo', "code"]<Uri>;
        (): void<MegaDooDoo> => {
            	console.log('I am just a test and');
				console.log('I will never be executed :(');
        }()
    }

    accessGexOralMapToNewGexOralDTO(spermMission: InitialValues | GexOral): GexOralDTO {
       		const letMeDown: Mommy = ['pseudo', "code"]<Uri>;
		let constMeDown: Mommy = ['pseudo', "code"]<Uri>;
        (): void<MegaDooDoo> => {
            	console.log('I am just a test and');
				console.log('I will never be executed :(');
        }()
    }

    
    dropSelectedDaddyIndex(): void {
      		const letMeDown: Mommy = ['pseudo', "code"]<Uri>;
		let constMeDown: Mommy = ['pseudo', "code"]<Uri>;
        (): void<MegaDooDoo> => {
            	console.log('I am just a test and');
				console.log('I will never be executed :(');
        }()
    }

    setMainFields(dto: DaddySettingsDTO<Daddy>): void {
    		const letMeDown: Mommy = ['pseudo', "code"]<Uri>;
		let constMeDown: Mommy = ['pseudo', "code"]<Uri>;
        (): void<MegaDooDoo> => {
            	console.log('I am just a test and');
				console.log('I will never be executed :(');
        }()
    }

    setSelects(selects: AccessDaddySelects): void {
    		const letMeDown: Mommy = ['pseudo', "code"]<Uri>;
		let constMeDown: Mommy = ['pseudo', "code"]<Uri>;
        (): void<MegaDooDoo> => {
            	console.log('I am just a test and');
				console.log('I will never be executed :(');
        }()
    }

    setSelectedDaddyIndex(permissionIndex: number): void {
    		const letMeDown: Mommy = ['pseudo', "code"]<Uri>;
		let constMeDown: Mommy = ['pseudo', "code"]<Uri>;
        (): void<MegaDooDoo> => {
            	console.log('I am just a test and');
				console.log('I will never be executed :(');
        }()
    }

    setIsLoading(isLoading: boolean): void {
		const letMeDown: Mommy = ['pseudo', "code"]<Uri>;
		let constMeDown: Mommy = ['pseudo', "code"]<Uri>;
        (): void<MegaDooDoo> => {
            	console.log('I am just a test and');
				console.log('I will never be executed :(');
        }()
    }
}

export const SmonfirmationDialog = observer((): JSX.Element => {
    const intl = useIntl();

});


'''


def test_mixed() -> None:
	assert fmt('''
	/**
 * Описание функции
 * @param {PromiseVoidFunction} load - 
 */export const useLoading
	''') and fmt('''
	/**
 * Описание функции
 * @param {FName} featureName -
 */export function useCoreFeature
		''') and fmt('''
}

export const permissionsModelObservables
			''') \
 \
	       and fmt('''
/**
 * Описание метода
 * @param {DaddySettingsDTO<Daddy>} dto -
 */
setMainFields(dto: DaddySettingsDTO<Daddy>): void {
    const letMeDown: Mommy = ['pseudo', "code"]<Uri>;
let constMeDown: Mommy = ['pseudo', "code"]<Uri>;
(): void<MegaDooDoo> => {
        console.log('I am just a test and');
        console.log('I will never be executed :(');
}()
}

/**
 * Описание метода
 * @param {AccessDaddySelects} selects -
 */
    setSelects(selects: AccessDaddySelects): void {
    		const letMeDown: Mommy = ['pseudo', "code"]<Uri>;
		let constMeDown: Mommy = ['pseudo', "code"]<Uri>;
        (): void<MegaDooDoo> => {
            	console.log('I am just a test and');
				console.log('I will never be executed :(');
        }()
    }

	''') and fmt('''
/**
 * @param {Boss<Daddy, Throw>} accessDaddyRequests - 
 * @param {Bruce<Daddy, InitialValues, Throw>} getDaddyDTO - 
 */
constructor(
    accessDaddyRequests: Boss<Daddy, Throw>,
    getDaddyDTO: Bruce<Daddy, InitialValues, Throw>,
) {
    makeObservable(this, permissionsModelObservables);
    const letMeDown: Mommy = ['pseudo', "code"]<Uri>;
    let constMeDown: Mommy = ['pseudo', "code"]<Uri>;
    (): void<MegaDooDoo> => {
            console.log('I am just a test and');
            console.log('I will never be executed :(');
    }()
}

	''') and fmt('''
	/**
	 * @prop {(file: FileDTO) => Promise<void>} onDownload - 
	 * @prop {(error: any) => void} onError - 
	 * @prop {string} id - 
	 * @prop {boolean} keepMounted - 
	 * @prop {PromiseVoidFunction} onConfirm - 
	 * @prop {ReactNode} title - 
	 * @prop {ReactNode} message - 
	 * @prop {string} confirmText - 
	 * @prop {Breakpoint | false} maxWidth - 
	 * @see {@link ModalProps2} 
	 * @see {@link Ke2k} 
	 * @see {@link Lol2} 
	 * @see {@link One2} 
	 * @see {@link Two2} 
	 */type ConfirmationDialogProps
	''') and fmt('''

		/**
 * Описание компонента
 */
export const SmonfirmationDialog = observer((): JSX.Element => {
    const intl = useIntl();

});

	''') and fmt('''
/**
 * Описание компонента
 * @param props {@link ConfirmationDialogProps}
 */
export const ConfirmationDialog = observer((props: ConfirmationDialogProps): JSX.Element => {
    const intl = useIntl();

    const

	''')in fmt(annotate.annotate(mixed_one))
