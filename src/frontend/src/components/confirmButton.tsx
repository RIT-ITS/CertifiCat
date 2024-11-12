import { LitElement, html } from "lit";
import { customElement, property, state } from "lit/decorators.js";

@customElement('confirm-button')
export class ConfirmButtonElement extends LitElement {
    @state()
    private showWarning = false
    @property()
    accessor warningText!:string;
    @property()
    accessor value!:string
    @property()
    accessor name!:string; 
    @property()
    accessor buttonType!:string;

    protected override createRenderRoot(): HTMLElement | DocumentFragment {
        return this;
    }

    protected override render() {
        if(this.showWarning) {
            return html`
                <p>${this.warningText}</p>
                <input
                    @click=${() => this.showWarning = false}
                    type="button"
                    value="Cancel" 
                    class="btn btn-secondary btn-primary" />
                <input
                    .name="${this.name}" 
                    .type="${this.buttonType || "button"}"
                    .value="${this.value}" 
                    class="btn btn-primary btn-danger" />
            `;
        }else{
            return html`
                <input
                    @click=${() => this.showWarning = true}
                    type="button"
                    .value="${this.value}" 
                    class="btn btn-primary btn-danger" />
            `;
        }
    }
}