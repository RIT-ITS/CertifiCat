import { LitElement } from "lit";
import { customElement, query } from "lit/decorators.js";

@customElement("profile-menu")
export class ProfileMenuElement extends LitElement {
    @query(".submenu-toggle")
    private submenuToggle!: HTMLElement;
    @query(".submenu")
    private submenu!: HTMLElement;

    protected override createRenderRoot(): HTMLElement | DocumentFragment {
        return this;
    }

    override connectedCallback(): void {
        super.connectedCallback();
        this.submenuToggle.addEventListener("mousedown", this.toggle);
        this.submenu.addEventListener("mousedown", this.submenuClick);
        document.addEventListener("mousedown", this.hide);
        document.addEventListener("scroll", this.hide);
    }

    private toggle = (evt: Event) => {
        if (this.classList.contains("profile--show")) {
            this.classList.remove("profile--show");
        } else {
            this.classList.add("profile--show");
        }

        evt.stopPropagation();
    };

    private submenuClick = (evt: Event) => {
        evt.stopPropagation();
    };

    private hide = () => {
        this.classList.remove("profile--show");
    };
}
