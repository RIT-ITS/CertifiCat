import { LitElement } from "lit";
import { customElement, property, query } from "lit/decorators.js";

@customElement("mobile-nav")
export class MobileNavElement extends LitElement {
    @property()
    accessor trigger!: string;
    triggerEl!: HTMLElement;
    @query("#close-mobile-navigation-link")
    closeLink!: HTMLElement;

    protected override createRenderRoot(): HTMLElement | DocumentFragment {
        return this;
    }

    override connectedCallback(): void {
        super.connectedCallback();
        this.triggerEl = document.querySelector(this.trigger)!;
        this.triggerEl.addEventListener("click", this.show);

        this.closeLink.addEventListener("click", this.hide);
        this.querySelector(".overlay")?.addEventListener("click", this.hide);
    }

    private show = () => {
        this.classList.remove("hidden");
    };

    private hide = () => {
        this.classList.add("hidden");
    };
}
