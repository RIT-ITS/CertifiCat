import { LitElement, html } from "lit";
import { ref, createRef, Ref } from 'lit/directives/ref.js';
import { customElement, property, state } from "lit/decorators.js";
import { getErrorMessage } from "../util";
import { Task, TaskStatus } from "@lit/task";

interface Group {
    id: number
    name: string
}

type GroupId = number;
type Operation = 'add' | 'del'

@customElement("account-access-manager")
export class AccountAccessManagerElement extends LitElement {
    @property()
    accessor groupFetchUrl!: string;
    @property()
    accessor groupUpdateUrl!: string;
    @property({type: Array})
    accessor accessibleBy!: Set<Group>;
    @state()
    accessor editMode = false;
    @state()
    accessor saving = false;
    
    @state()
    accessor error: string | null = null;

    @state()
    accessor loadGroupsTask = new Task(this, {
        autoRun: false,
        task: async() => {
            const result = await fetch(this.groupFetchUrl, {
                method: "GET",
                credentials: "same-origin",
            });
            
            if(result.status !== 200) {
                throw new Error(`${result.status} status code returned from endpoint`);
            }
    
            try {
                return (await result.json()) as Group[];
            }catch{
                throw new Error("Unexpected result returned from endpoint");
            }
        }
    })

    @state()
    accessor modifyGroupsTask = new Task(this, {
        autoRun: false,
        
        task: async(args: [Operation, GroupId]) => {
            const [operation, groupId] = args;
            const group = this.loadGroupsTask.value!.find((group) => group.id == groupId);
            if(!group) {
                throw Error("Unknown error");
            }

            const existingGroup = Array.from(this.accessibleBy).find((group) => group.id == groupId);
            if(operation == 'add' && existingGroup) {
                return;
            }

            const result = await fetch(this.groupUpdateUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    "groups": {
                        [operation]: [groupId]
                    }
                }),
                credentials: "same-origin",
            });
            
            if(result.status !== 200) {
                throw new Error(`${result.status} status code returned from endpoint`);
            }

            if(operation == 'add') {
                this.accessibleBy = this.accessibleBy.add(group);
            }else{
                this.accessibleBy.delete(existingGroup!);
                this.accessibleBy = new Set(this.accessibleBy);
            }
        }
    })

    accessor editableWrap!: HTMLDivElement;

    protected override createRenderRoot(): HTMLElement | DocumentFragment {
        return this;
    }

    override connectedCallback(): void {
        super.connectedCallback();
        this.accessibleBy = new Set(this.accessibleBy);
    }

    private transitionToEdit = async () => {
        if(this.editMode) return;
        this.editMode = true;

        try {
            await this.loadGroupsTask.run()
        }catch(exc) {
            this.error = getErrorMessage(exc);
            this.editMode = false;
        }
    }

    private transitionToReadonly = () => {
        this.editMode = false;
    }

    private addGroup = (groupId: number) => {
        this.modifyGroupsTask.run(['add' as Operation, groupId])
    }

    private removeGroup = (groupId: number) => {
        this.modifyGroupsTask.run(['del' as Operation, groupId])
    }

    protected override render() {
        return html`
            ${this.renderError()}
            <div class="row">
                ${this.renderHeader()}
                ${this.renderEditButton()}
                ${this.renderCancelButton()}
            </div>
            ${this.editMode ?
                this.loadGroupsTask.render({
                    complete: (groups) => {
                        if(groups.length > 0) {
                            return html`
                                ${this.renderGroupDisplay()}
                                ${this.renderAdd()}
                            `;
                        }else{
                            return html`<b class='bold'>You're not in any groups</b>`;
                        }
                    }
                }) : this.renderGroupDisplay()
            }
        `
    }

    protected renderError() {
        const err = (this.loadGroupsTask.error ?? this.modifyGroupsTask.error) as Error | null;

        return err ? html`<div class='messages messages--error messages-small mb-2'>${err.message}</div>` : null;
    }

    protected renderHeader() {
        return html`<div class="accessmanager--header">${this.accessibleBy.size > 0 ? 'Group Membership' : 'Creator Only'}</div>`
    }

    protected renderGroupDisplay() {
        return html`
            <ul>
            ${Array.from(this.accessibleBy).map((group) => {
                return html`<li>
                                <span class="mr-2"><i class="fa-solid fa-user-group"></i></span>
                                <span class="accessmanager--groupname">${group.name}</span>
                                ${this.editMode ? html`<a
                                    href="javascript:return false;"
                                    class="accessmanager--edit"
                                    @click="${() => this.removeGroup(group.id)}"
                                >
                                    &nbsp;<span class="fa-solid fa-trash fa-lg"></span>
                                </a>` : null}
                            </li>`
            })}
            </ul>
        `
    }

    protected renderEditButton() {
        if(this.editMode) return null;

        return html`<a
                    href="javascript:return false;"
                    class="accessmanager--edit"
                    @click="${this.transitionToEdit}"
                >
                    Edit &nbsp;<span class="fa-regular fa-pen-to-square"></span>
                </a>`
    }

    protected renderCancelButton() {
        if(!this.editMode) return null;

        return html`<a
                    href="javascript:return false;"
                    class="accessmanager--cancel"
                    @click="${this.transitionToReadonly}"
                >
                    Stop Editing &nbsp;<span class="fa-solid fa-backward"></span>
                </a>`
    }

    protected renderAdd() {
        if(!this.editMode || this.loadGroupsTask.status != TaskStatus.COMPLETE) return null;

        const selectRef: Ref<HTMLSelectElement> = createRef();
        return html`<div class="accessmanager--add">
                        <select ${ref(selectRef)}>
                            ${this.loadGroupsTask.value!.map((group) => html`
                                <option value="${group.id}">${group.name}</option>
                            `)}
                        </select>
                        <a @click="${() => this.addGroup(Number(selectRef.value!.value))}" class="btn btn-primary-outline btn-sm">Add</a>
                    </div>`
    }

}
