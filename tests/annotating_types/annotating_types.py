from annotate import annotate
from annotate.utils.utils import fmt

type_one: str = '''type ConfirmationDialogProps = ModalProps &
    Kek &
    Lol &
    One &
    Two & {
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
'''

type_two: str = '''type ConfirmationDialogProps = ModalPro3ps & {
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
'''

type_three: str = '''type ConfirmationDialogProps = ModalProps2 &
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
'''

type_four: str = '''type ConfirmationDialogProps = {
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
'''


def test_types() -> None:
	assert fmt('''
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
	 * @see {@link ModalProps} 
	 * @see {@link Kek} 
	 * @see {@link Lol} 
	 * @see {@link One} 
	 * @see {@link Two} 
	 */type ConfirmationDialogProps
	''') in fmt(annotate.annotate_type(type_one))

	assert fmt('''
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
	 * @see {@link ModalPro3ps} 
	 */type ConfirmationDialogProps
	''') in fmt(annotate.annotate_type(type_two))

	assert fmt('''
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
	''') in fmt(annotate.annotate_type(type_three))

	assert fmt('''
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
	 */type ConfirmationDialogProps
	''') in fmt(annotate.annotate_type(type_four)) and fmt("@see {@link ModalProps2} ") not in fmt(
		annotate.annotate_type(type_four))
