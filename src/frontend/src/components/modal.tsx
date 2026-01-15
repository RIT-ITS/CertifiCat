import { LitElement, PropertyValues, html } from "lit";
import { customElement, property, query, queryAll } from "lit/decorators.js";

// This class is an awkward wrapper around the new account form, its purpose is to encapsulate the new account
// form code in one place, but this is not a good example of using Lit

@customElement("form-modal")
export class FormModal extends LitElement {
    @property()
    accessor trigger!: string;
    triggerEl!: HTMLElement;

    @property()
    accessor header!: string;

    @property()
    accessor addButtonText!: string;

    @property()
    accessor addButtonName!: string;

    @property()
    accessor autoFocus: string | undefined = undefined;

    @query(".modal")
    modal!: HTMLElement;

    @query(".modal--content")
    modalContent!: HTMLElement;

    @queryAll(".modal-close")
    closeLinks!: NodeListOf<HTMLElement>;

    contactContainer!: HTMLElement;

    constructor() {
        super();
    }

    override connectedCallback(): void {
        super.connectedCallback();
        this.triggerEl = document.querySelector(this.trigger)!;
        this.triggerEl.addEventListener("click", this.show);
    }

    protected override firstUpdated(_changedProperties: PropertyValues): void {
        super.firstUpdated(_changedProperties);

        this.closeLinks.forEach(el => el.addEventListener("click", this.hide));
        this.modalContent.addEventListener("click", (evt) => {
            evt.stopPropagation();
            return false;
        })
    }

    private show = () => {
        this.modal.classList.add("modal--shown");
        if(this.autoFocus) {
            (this.querySelector(this.autoFocus) as HTMLInputElement)?.focus();
        }
    };

    private hide = () => {
        this.modal.classList.remove("modal--shown");
    };

    protected override createRenderRoot(): HTMLElement | DocumentFragment {
        return this;
    }

    override render() {
        return html`
            <form action="." method="post">
                <div class="modal">
                    <div class="modal--container modal-close">
                        <div class="modal--content">
                            <div class="modal--header modal--header--custom px-3 py-3">
                                <h3 class="bold mb-0">${this.header}</h3>
                                <a class="btn btn--light btn--md bg-gray-500 modal-close"><i class="fa-solid fa-close"></i></a>
                            </div>
                            <div class="modal--body px-3 py-3">
                                ${this.children}
                            </div>
                            <div class="modal--footer px-3 py-3">
                                <div class="modal--footer--custom">
                                    <div class="modal--footer--buttons rtl-buttons">
                                        <input 
                                            class="btn btn--primary btn--md" 
                                            type="submit"
                                            name="${this.addButtonName}" 
                                            value="${this.addButtonText}" />
                                        <a class="btn btn--primary btn--md btn--primary-outline modal-cancel modal-close">Cancel</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </form>
        `;
    }
}
