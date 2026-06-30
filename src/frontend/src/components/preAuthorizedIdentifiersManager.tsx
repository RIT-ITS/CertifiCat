import { LitElement, html } from "lit";
import { ref, createRef, Ref } from 'lit/directives/ref.js';
import { customElement, property, state } from "lit/decorators.js";
import { getCsrfToken } from "../util";
import { Task } from "@lit/task";

interface Identifier {
    name: string
}

type Operation = 'add' | 'del'

@customElement("pre-authorized-identifiers-manager")
export class PreAuthorizedIdentifiersManagerElement extends LitElement {
    @property()
    accessor updateUrl!: string;
    @property({type: Array})
    accessor identifiers!: Set<Identifier>;
    @property()
    accessor canEdit!: boolean;

    @state()
    accessor editMode = false;
    @state()
    accessor saving = false;
    

    @state()
    accessor error: string | null = null;

    @state()
    accessor modifyIdentifiersTask = new Task(this, {
        autoRun: false,
        
        task: async(args: [Operation, Identifier]) => {
            const [operation, identifier] = args;
            const existingIdentifier = Array.from(this.identifiers).find((i) => i.name == identifier.name);

            if(operation == 'add' && existingIdentifier) {
                return;
            }

            const result = await fetch(this.updateUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCsrfToken()!,
                },
                body: JSON.stringify({
                    [operation]: [identifier.name]
                }),
                credentials: "same-origin",
            });
            
            if(result.status == 400) {
                throw new Error((await result.json()).error);
            }
            if(result.status !== 200) {
                throw new Error(`${result.status} status code returned from endpoint`);
            }

            if(operation == 'add') {
                this.identifiers = this.identifiers.add(identifier);
            }else{
                this.identifiers.delete(existingIdentifier!);
                this.identifiers = new Set(this.identifiers);
            }
        }
    })

    accessor editableWrap!: HTMLDivElement;

    protected override createRenderRoot(): HTMLElement | DocumentFragment {
        return this;
    }

    override connectedCallback(): void {
        super.connectedCallback();
        this.canEdit = String(this.canEdit).toLowerCase() === "true"
        this.identifiers = new Set(this.identifiers);
    }

    private transitionToEdit = async () => {
        if(this.editMode) return;
        this.editMode = true;
    }

    private transitionToReadonly = () => {
        this.editMode = false;
    }

    private addIdentifier = (name: string) => {
        this.modifyIdentifiersTask.run(['add' as Operation, {name}])
    }

    private removeIdentifier = (name: string) => {
        this.modifyIdentifiersTask.run(['del' as Operation, {name}])
    }

    protected override render() {
        return html`
            ${this.renderError()}
            <div class="flex">
                ${this.renderHeader()}
                ${this.renderEditButton()}
                ${this.renderCancelButton()}
            </div>

            ${this.renderIdentifierDisplay()}
            ${this.renderAdd()}
        `
    }

    protected renderError() {
        const err = (this.modifyIdentifiersTask.error) as Error | null;

        return err ? html`<div class='message message--error message-small mb-2'>${err.message}</div>` : null;
    }

    protected renderHeader() {
        if(this.canEdit) {
            return html`<div class="identifiermanager--header mb-2">Manage Pre-Authorizations</div>`
        }

        return null;
    }

    protected renderIdentifierDisplay() {
        return html`
            <ul>
            ${Array.from(this.identifiers).map((identifier) => {
                return html`<li>
                                <span class="mr-2"><i class="fa-solid fa-unlock"></i></span>
                                <span class="identifiermanager--name">${identifier.name}</span>
                                ${this.editMode ? html`<a
                                    href="javascript:return false;"
                                    class="identifiermanager--edit"
                                    @click="${() => this.removeIdentifier(identifier.name)}"
                                >
                                   &nbsp;<span class="fa-solid fa-trash fa-lg"></span>
                                </a>` : null}
                            </li>`
            })}
            </ul>
        `
    }

    protected renderEditButton() {
        if(!this.canEdit) return null;
        if(this.editMode) return null;

        return html`<a
                    href="javascript:return false;"
                    class="identifiermanager--edit"
                    @click="${this.transitionToEdit}"
                >
                    Edit &nbsp;<span class="fa-regular fa-pen-to-square"></span>
                </a>`
    }

    protected renderCancelButton() {
        if(!this.editMode) return null;

        return html`<a
                    href="javascript:return false;"
                    class="identifiermanager--cancel"
                    @click="${this.transitionToReadonly}"
                >
                    Stop Editing &nbsp;<span class="fa-solid fa-backward"></span>
                </a>`
    }

    protected renderAdd() {
        if(!this.editMode) return null;

        const inputRef: Ref<HTMLInputElement> = createRef();
        return html`<div class="identifiermanager--add">
                        <input name="identifier" placeholder="domain.acme.com" ${ref(inputRef)} />
                        <a @click="${() => this.addIdentifier(inputRef.value!.value)}" class="btn btn--primary btn--outline btn--sm">Add</a>
                    </div>`
    }

}
