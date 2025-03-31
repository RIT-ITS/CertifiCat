import { LitElement, html } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import { classMap } from "lit/directives/class-map.js";

@customElement("editable-text")
export class EditableTextElement extends LitElement {
    @property()
    accessor editButtonText = "Edit";
    @property()
    accessor editButtonDisplay: "button"|"link" = "button"
    @property()
    accessor actionButtonDisplay: "button"|"link" = "button"
    @property()
    accessor url!: string;
    @state()
    accessor editMode = false;
    @state()
    accessor contentBeforeEditing = new Map<string, string>();
    @state()
    accessor saving = false;

    accessor editableWrap!: HTMLDivElement;

    protected override createRenderRoot(): HTMLElement | DocumentFragment {
        return this;
    }

    private editableElements(): Map<string, HTMLElement> {
        var editableElementMapping = new Map<string, HTMLElement>();
        this.querySelectorAll(".edit-wrap>[data-editable-id]").forEach((el) => {
            editableElementMapping.set(
                el.getAttribute("data-editable-id")!,
                el as HTMLElement
            );
        });
        return editableElementMapping;
    }

    override connectedCallback(): void {
        super.connectedCallback();
        this.editableWrap = document.createElement("div");
        this.editableWrap.classList.add("edit-wrap");
        while (this.childNodes.length > 0) {
            this.editableWrap.appendChild(this.childNodes[0]);
        }

        this.replaceChildren(this.editableWrap);
    }

    private transitionToEdit = () => {
        this.classList.add("editing");
        this.editMode = true;
        this.editableElements().forEach((value, key) => {
            this.contentBeforeEditing.set(key, value.innerHTML || "");
            try {
                value.contentEditable = "plaintext-only";
            }catch{
                value.contentEditable = "true";
            }
            value.focus();
        });
    };

    private cancelEdit = () => {
        this.editableElements().forEach((value, key) => {
            value.innerHTML = this.contentBeforeEditing.get(key)!;
        });

        this.transitionToReadonly();
    };

    private transitionToReadonly = () => {
        this.classList.remove("editing");
        this.editMode = false;
        this.editableElements().forEach((value) => {
            value.contentEditable = "false";
        });
    };

    private save = async () => {
        if (this.saving) return;
        this.saving = true;

        var body: { [key: string]: string } = {};
        this.editableElements().forEach((value, key) => {
            value.contentEditable = "false";
            body[key] = value.innerText = value.innerText.trim();
        });

        let error = false;

        try {
            const result = await fetch(this.url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(body),
                credentials: "same-origin",
            });

            error = result.status !== 200;
        } catch {
            error = true;
        }

        this.saving = false;
        if (error) {
            this.editableElements().forEach((value) => {
                try {
                    value.contentEditable = "plaintext-only";
                }catch{
                    value.contentEditable = "true";
                }
            });
            alert("There was an error saving");
        } else {
            this.transitionToReadonly();
        }
    };

    protected override render() {
        return html` <div class="buttons">${this.renderButtons()}</div> `;
    }

    private renderButtons() {
        if (this.editMode) {
            const cancelClasses = {
                'cancel': true,
                'btn': this.actionButtonDisplay == 'button',
                'btn-light': this.actionButtonDisplay == 'button',
                'btn-sm': this.actionButtonDisplay == 'button'
            }

            const saveClasses = {
                'save': true,
                'btn': this.actionButtonDisplay == 'button',
                'btn-primary': this.actionButtonDisplay == 'button',
                'btn-sm': this.actionButtonDisplay == 'button'
            }

            return html`
                <a
                    href="javascript:return false;"
                    ?disabled="${this.saving}"
                    class="${classMap(cancelClasses)}"
                    @click="${this.cancelEdit}"
                >
                    Cancel &nbsp;<span class="fa-solid fa-backward"></span>
                </a>
                <a
                    href="javascript:return false;"
                    ?disabled="${this.saving}"
                    class="${classMap(saveClasses)}"
                    @click="${this.save}"
                >
                    Save &nbsp;<span class="fa-solid fa-floppy-disk"></span>
                </a>
            `;
        } else {
            const editClasses = {
                'btn': this.editButtonDisplay == 'button',
                'btn-primary': this.editButtonDisplay == 'button',
                'btn-sm': this.editButtonDisplay == 'button'
            }

            return html`
                <a
                    href="javascript:return false;"
                    class="${classMap(editClasses)}"
                    @click="${this.transitionToEdit}"
                >
                    ${this.editButtonText} &nbsp;<span class="fa-regular fa-pen-to-square"></span>
                </a>
            `;
        }
    }
}
