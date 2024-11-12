import { LitElement } from "lit";
import { customElement } from "lit/decorators.js";

@customElement("sticky-nav")
export class StickyNavElement extends LitElement {
    topPadding = 0;

    protected override createRenderRoot(): HTMLElement | DocumentFragment {
        return this;
    }

    override connectedCallback(): void {
        this.topPadding = parseFloat(window.getComputedStyle(this).paddingTop);
        window.addEventListener("scroll", this.onScroll);
        super.connectedCallback();

        this.onScroll();
    }

    protected onScroll = () => {
        if (this.topPadding < window.scrollY) {
            this.classList.add("minimized");
        } else {
            this.classList.remove("minimized");
        }
    };
}
