import { LitElement, PropertyValues, html, render } from "lit";
import { customElement, property, query, queryAll } from "lit/decorators.js";

// This class is an awkward wrapper around the new account form, its purpose is to encapsulate the new account
// form code in one place, but this is not a good example of using Lit

@customElement("portal-modal")
export class FormModal extends LitElement {
    @property()
    accessor header!: string;

    @query(".modal")
    modal!: HTMLElement;

    @query(".modal--content")
    modalContent!: HTMLElement;

    private modalContainer:HTMLDivElement | null = null;

    constructor() {
        super();
    }

    override connectedCallback(): void {
        super.connectedCallback();
        this.modalContainer = document.createElement('div')
    }

    private permissionModal = () =>  html`<div class="modal modal--shown">
        <div class="modal--container modal-close ">
            <div class="modal--content">
                <div class="modal--header modal--header--custom px-3 py-3">
                    <h3 class="bold mb-0">${this.header}</h3>
                </div>
                <div class="modal--body px-3 py-3">
                    ${this.children}
                </div>
                
            </div>
        </div>
    </div>`

    protected override firstUpdated(_changedProperties: PropertyValues): void {
        document.body.appendChild(this.modalContainer!);
        render(this.permissionModal(), this.modalContainer!)
    }    

    protected override createRenderRoot(): HTMLElement | DocumentFragment {
        return this;
    }

    override render() {
        return null;
    }
}
