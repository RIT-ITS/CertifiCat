import { LitElement, PropertyValues, html, render } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import { when } from 'lit/directives/when.js'
import { getCsrfToken, getErrorMessage } from "../util";

interface Owner {
    username: string;
    first_name: string;
    last_name: string;
    email: string;
}

@customElement("owner-manager")
export class OwnerManagerElement extends LitElement {
    @property()
    accessor ownerUpdateUrl!: string;
    @property()
    accessor owner = "";
    @property({type: Boolean})
    accessor readonly = false;

    @state()
    accessor editMode = false;
    @state()
    accessor username = "";
    @state()
    accessor saving = false;
    @state()
    accessor error: string | null = null;
    @state()
    accessor ownerDetails: Owner | null = null;
    @state()
    accessor accessChanged = false;

    private modalContainer:HTMLDivElement | null = null;
    private initialOwner: Node[] | undefined;

    override connectedCallback(): void {
        if(!this.initialOwner) {
            this.initialOwner = Array.from(this.childNodes);
            this.replaceChildren();
        }
        this.modalContainer = document.createElement('div')
        super.connectedCallback();
    }

    override disconnectedCallback(): void {
        this.modalContainer?.remove();
    }

    protected override createRenderRoot(): HTMLElement | DocumentFragment {
        return this;
    }

    private transitionToEdit = () => {
        if(this.readonly || this.saving) return;
        this.username = "";
        this.error = null;
        this.editMode = true;
    }

    private transitionToReadonly = () => {
        if(this.saving) return;
        this.editMode = false;
        this.username = "";
        this.error = null;
    }

    private transferOwnership = async (event: SubmitEvent) => {
        event.preventDefault();
        const owner = this.username.trim();
        if(this.readonly || this.saving || !owner) return;

        this.saving = true;
        this.error = null;
        try {
            const result = await fetch(this.ownerUpdateUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCsrfToken()!,
                },
                body: JSON.stringify({owner}),
                credentials: "same-origin",
            });

            if(result.status === 400) {
                throw new Error((await result.json()).error);
            }
            if(result.status !== 200) {
                throw new Error(`${result.status} status code returned from endpoint`);
            }

            const data = await result.json() as {owner: Owner, can_transfer: boolean};
            this.ownerDetails = data.owner;
            this.owner = data.owner.username;
            this.editMode = false;
            this.username = "";

            if(!data.can_transfer) {
                this.accessChanged = true;
            }
        }catch(error) {
            this.error = getErrorMessage(error);
        }finally {
            this.saving = false;
        }
    }

    private reloadRequired = () => html`
        <portal-modal header="Reload Required">
            <p>Your access to this resource has changed. Please reload the page.</p>
        </portal-modal>`

    protected override render() {
        return html`
            ${when(this.accessChanged, this.reloadRequired)}
            ${this.error ? html`<div role="alert" class="message message--error message-small mb-2">${this.error}</div>` : null}
            <div class="flex">
                <div>
                    ${this.ownerDetails ? html`
                        <b class="bold">${this.ownerDetails.first_name
                            ? `${this.ownerDetails.first_name} ${this.ownerDetails.last_name}`
                            : this.ownerDetails.username}</b><br />
                        ${this.ownerDetails.email}
                    ` : this.initialOwner?.length ? this.initialOwner : html`<b class="bold">${this.owner}</b>`}
                </div>
                ${!this.readonly && !this.editMode ? html`
                    <a href="javascript:return false;" @click=${this.transitionToEdit}>
                        Edit &nbsp;<span class="fa-regular fa-pen-to-square"></span>
                    </a>
                ` : null}
                ${this.editMode ? html`
                    <a href="javascript:return false;" ?disabled=${this.saving} @click=${this.transitionToReadonly}>
                        Stop Editing &nbsp;<span class="fa-solid fa-backward"></span>
                    </a>
                ` : null}
            </div>
            ${this.editMode ? html`
                <form class="ownermanager--form" @submit=${this.transferOwnership}>
                    <input name="owner" aria-label="New owner's username" placeholder="Username" required
                        .value=${this.username} ?disabled=${this.saving}
                        @input=${(event: Event) => this.username = (event.target as HTMLInputElement).value} />
                    <button type="submit" class="btn btn--primary btn--outline btn--sm"
                        ?disabled=${this.saving || !this.username.trim()}>
                        Transfer Ownership
                    </button>
                </form>
            ` : null}
        `;
    }
}
