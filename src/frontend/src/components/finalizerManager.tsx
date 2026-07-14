import { LitElement, html } from "lit";
import { ref, createRef, Ref } from 'lit/directives/ref.js';
import { customElement, property, state } from "lit/decorators.js";
import { getCsrfToken } from "../util";
import { Task } from "@lit/task";
import { map } from 'lit/directives/map.js';

interface Finalizer {
    name: string
    description: string
}


@customElement("finalizer-manager")
export class FinalizerManagerElement extends LitElement {
    @property()
    accessor updateUrl!: string;
    @property({type: Object})
    accessor finalizers!: Map<string, Finalizer>;
    @property()
    accessor canEdit!: boolean;
    @property()
    accessor selectedFinalizer!: string;
    @property()
    accessor defaultFinalizer!: string;

    @state()
    accessor editMode = false;
    @state()
    accessor saving = false;
    

    @state()
    accessor error: string | null = null;

    @state()
    accessor modifyFinalizerTask = new Task(this, {
        autoRun: false,
        
        task: async(args: [string]) => {
            const [finalizerId] = args;
            
            const result = await fetch(this.updateUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCsrfToken()!,
                },
                body: JSON.stringify({
                    'id': finalizerId
                }),
                credentials: "same-origin",
            });
            
            if(result.status == 400) {
                throw new Error((await result.json()).error);
            }
            if(result.status !== 200) {
                throw new Error(`${result.status} status code returned from endpoint`);
            }

            this.selectedFinalizer = finalizerId;
            this.transitionToReadonly()
        }
    })

    accessor editableWrap!: HTMLDivElement;

    protected override createRenderRoot(): HTMLElement | DocumentFragment {
        return this;
    }

    override connectedCallback(): void {
        super.connectedCallback();
        this.canEdit = String(this.canEdit).toLowerCase() === "true";
        this.finalizers = new Map(Object.entries(this.finalizers));
        if(!this.selectedFinalizer) {
            this.selectedFinalizer = this.defaultFinalizer;
        }
    }

    private currentFinalizer = () => {
        return this.finalizers.get(this.selectedFinalizer) ?? this.finalizers.get(this.defaultFinalizer)!;
    }

    private transitionToEdit = async () => {
        if(this.editMode) return;
        this.editMode = true;
    }

    private transitionToReadonly = () => {
        this.editMode = false;
    }

    protected override render() {
        return html`
            ${this.renderMissingFinalizerError()}
            ${this.renderError()}
            <div class="flex">
                ${this.renderHeader()}
                ${this.renderEditButton()}
                ${this.renderCancelButton()}
                <div class="finalizermanager--description">
                    ${this.currentFinalizer().description}
                </div>
            </div>

            ${this.renderAdditionalFinalizers()}
        `
    }

    protected renderMissingFinalizerError() {
        if(!this.finalizers.has(this.selectedFinalizer)) {
            return html`<div class='message message--error message-small mb-2'>This account is configured to use missing finalizer '${this.selectedFinalizer}'.</div>`;
        }

        return null;
    }

    protected renderError() {
        const err = (this.modifyFinalizerTask.error) as Error | null;

        return err ? html`<div class='message message--error message-small mb-2'>${err.message}</div>` : null;
    }

    protected renderHeader() {
        return html`<div class="finalizermanager--header mb-2 bold">
            ${this.currentFinalizer().name}
        </div>`
    }

    protected renderAdditionalFinalizers() {
        if(!this.editMode) return null;

        const finalizerKeys = Array.from(this.finalizers.keys()).filter(k => k != this.defaultFinalizer);
        finalizerKeys.unshift(this.defaultFinalizer);

        const orderedFinalizers = new Map(finalizerKeys.map(key => [key, this.finalizers.get(key)!]));

        return html`<ul>
            ${map(
                orderedFinalizers.entries(),
                ([id, finalizer]) => id != this.selectedFinalizer ? html`<li>
                    <a @click="${() => this.modifyFinalizerTask.run([id])}">
                        <div class="finalizermanager--option">
                            <h4>${finalizer.name}</h4>
                            ${finalizer.description}
                        </div>
                        <span><i class="fa-solid fa-chevron-right"></i></span>
                    </a>
                </li>` : null
            )}
        </ul>`

    }

    protected renderEditButton() {
        if(!this.canEdit) return null;
        if(this.editMode) return null;

        return html`<a
                    href="javascript:return false;"
                    class="finalizermanager--edit"
                    @click="${this.transitionToEdit}"
                >
                    Change &nbsp;<span class="fa-regular fa-pen-to-square"></span>
                </a>`
    }

    protected renderCancelButton() {
        if(!this.editMode) return null;

        return html`<a
                    href="javascript:return false;"
                    class="finalizermanager--cancel"
                    @click="${this.transitionToReadonly}"
                >
                    Stop Editing &nbsp;<span class="fa-solid fa-backward"></span>
                </a>`
    }

 

}
