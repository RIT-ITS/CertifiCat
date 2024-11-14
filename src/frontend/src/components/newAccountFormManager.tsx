import { LitElement, html } from "lit";
import { customElement, query, queryAll } from "lit/decorators.js";

// This class is an awkward wrapper around the new account form, its purpose is to encapsulate the new account
// form code in one place, but this is not a good example of using Lit

@customElement("new-account-form-manager")
export class NewAccountFormManagerElement extends LitElement {
    @query("form")
    form!: HTMLFormElement;

    @query("#id_scope_1")
    groupScope?: HTMLInputElement;

    @query("#id_group")
    group!: HTMLSelectElement;

    @query("label[for=id_group]")
    groupLabel!: HTMLLabelElement;

    @queryAll("[name=scope]")
    scopes!: Array<HTMLInputElement>;

    contactContainer!: HTMLElement;

    constructor() {
        super();
    }

    override connectedCallback(): void {
        super.connectedCallback();
        this.setupEvents();

        this.setGroupVisibility();
    }

    private setupEvents() {
        this.scopes.forEach((scope) =>
            scope.addEventListener("change", this.setGroupVisibility)
        );
        
    }

    private setGroupVisibility = () => {
        this.group.style.display = this.groupScope?.checked ? "block" : "none";
        this.groupLabel.style.display = this.groupScope?.checked
            ? "block"
            : "none";
    };

   

    protected override createRenderRoot(): HTMLElement | DocumentFragment {
        return this;
    }

    override render() {
        return html` ${this.children} `;
    }
}
