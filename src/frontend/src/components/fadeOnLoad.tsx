import { LitElement } from "lit";
import { customElement } from "lit/decorators.js";

@customElement("fade-on-load")
export class FadeOnLoadElement extends LitElement {
    protected override createRenderRoot(): HTMLElement | DocumentFragment {
        return this;
    }

    override connectedCallback(): void {
        super.connectedCallback();
        this.classList.add("loaded");
    }
}
