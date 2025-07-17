import { LitElement, html } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import { Task, TaskStatus } from "@lit/task";
import { classMap } from "lit/directives/class-map.js";

interface OrderHistoryEvent {
    source: {
        content_type: number
        object_id: number
    }
    created_at: string
    ip_address: string | null
    user_agent: string | null
    event_type: string
    event_type_display: string
    payload: {[id:string]:string} | null
}

interface OrderHistory {
    events: OrderHistoryEvent[]
    sources: {[content_type_id:string]: {
        [id:string]: {
            id: number
            name: string | null
            repr: string
        }
    }}
}

const delay = (ms:number) => new Promise(resolve => setTimeout(resolve, ms));

@customElement("order-history")
export class OrderHistoryElement extends LitElement {
    @property()
    accessor url!: string;

    @state()
    accessor loadHistoryTask = new Task(this, {
        autoRun: false,
        task: async() => {
            const [result, _] = await Promise.all([fetch(this.url, {
                method: "GET",
                credentials: "same-origin"
            }), delay(1000)]);

            if(result.status !== 200) {
                throw new Error(`${result.status} status code returned from endpoint`)
            }

            try {
                return (await result.json()) as OrderHistory;
            }catch{
                throw new Error("Unexpected result returned from endpoint");
            }
        }
    })

    protected override createRenderRoot(): HTMLElement | DocumentFragment {
        return this;
    }

    override connectedCallback(): void {
        super.connectedCallback();
    }

    protected override render() {
        const refreshIconClasses = {
                'fa-solid': true,
                'fa-refresh': true,
                'refresh-button': true,
                'fa-spin': this.loadHistoryTask.status == TaskStatus.PENDING
            }

        return html`
        <h4 class='icon'><i class="fa-solid fa-clock"></i>
            Event History
            <i class="${classMap(refreshIconClasses)}" @click="${this.reload}"></i>
        </h4>
        ${this.renderHistoryEvents()}
        `;
    }

    protected renderHistoryEvents = () => {
        let history = this.loadHistoryTask.value;
        if(history) {
            return html`
                <div class="history--tablewrap">
                    <table class="table table--light">
                        <thead class="thead-light">
                            <tr>
                                <th>Event Time</th>
                                <th>Resource</th>
                                <th>Description</th>
                                <th>Payload</th>
                            </tr>
                        </thead>
                        
                        ${history.events.map((event) => this.renderEventRow(history, event))}
                    </table>
                </div>`
        }else{
            switch(this.loadHistoryTask.status) {
                case TaskStatus.INITIAL:
                    return html`<div>History hasn't been loaded. Refresh the history to see events.`;
                case TaskStatus.PENDING:
                    return html`<div>Loading history...</div>`;
                case TaskStatus.ERROR:
                    return html`<div>There was an error loading history.`;
            }
        }

        return null;
    }

    protected renderEventRow = (history:OrderHistory, event:OrderHistoryEvent) => {
        return html`
        <tr>
            <td class="shrink-cell">${new Date(event.created_at).toISOString()}</td>
            <td class="shrink-cell">${this.renderAssociatedObject(history, event)}</td>
            <td>${event.event_type_display}</td>
            <td>${this.renderPayload(event.payload)}</td>
        </tr>`
    }

    protected renderAssociatedObject = (history: OrderHistory, event: OrderHistoryEvent) => {
        try {
            let source = history.sources[event.source.content_type][event.source.object_id]
            return source.repr;
        }catch{
            return html`<i>repr not found</i>`;
        }
    }

    protected renderPayload = (payload: {
        [id: string]: string;
    } | null) => {
        if(payload) {
            return Object.entries(payload).map(([key, value]) => {
                return html`
                    ${key}: ${value} <br />
                `
            })
        }else{
            return null;
        }
    }

    protected renderHistory = async () => {
        if(this.loadHistoryTask.status == TaskStatus.INITIAL) return;
    }

    protected reload = () => {
        if(this.loadHistoryTask.status != TaskStatus.PENDING) {
            this.loadHistoryTask.run();
        }
    }
}
