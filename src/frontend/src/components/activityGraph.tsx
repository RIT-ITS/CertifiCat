import { Task, TaskStatus } from "@lit/task";
import { LitElement, html } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import * as color from "../color";
import { classMap } from "lit/directives/class-map.js";


@customElement("activity-graph")
export class ActivityGraphElement extends LitElement {
    @property()
    accessor url!: string;
    @property()
    accessor startActivityColor!: string;
    @property()
    accessor endActivityColor!: string;
    @property()
    accessor noActivityColor!: string;

    accessor colorSteps: Array<string> = [];

    @state()
    accessor loadActivityTask = new Task(this, {
        autoRun: false,
        task: async() => {
            const result = await fetch(this.url, {
                method: "GET",
                credentials: "same-origin"
            });

            if(result.status !== 200) {
                throw new Error(`${result.status} status code returned from endpoint`)
            }

            try {
                return (await result.json()) as {[id:string]:number};
            }catch{
                throw new Error("Unexpected result returned from endpoint");
            }
        }
    })

    monthAbbreviations:{[id:number]:string} = {
        0: "Jan",
        1: "Feb",
        2: "Mar",
        3: "Apr",
        4: "May",
        5: "Jun",
        6: "Jul",
        7: "Aug",
        8: "Sep",
        9: "Oct",
        10: "Nov",
        11: "Dec"
    }

    daysInMonth(date:Date) {
        return new Date(date.getFullYear(), date.getMonth()+1, 0).getDate();
    }

    override connectedCallback(): void {
        super.connectedCallback();
        for(let i=1;i<=3;i++) {
            this.colorSteps[i] = color.blendColors(this.startActivityColor, this.endActivityColor, (i-1)/2);
        }
    }

    protected override createRenderRoot(): HTMLElement | DocumentFragment {
        return this;
    }

    protected override render() {
        window.requestAnimationFrame(this.renderSquares);
        const classes = {
            'heat-calendar': true,
            'loading': this.loadActivityTask.status != TaskStatus.COMPLETE,
            'error': this.loadActivityTask.status == TaskStatus.ERROR
        }
        return html`<div class="${classMap(classes)}">
                        <ul class="heat-calendar__months"></ul>
                        <ul class="heat-calendar__days">
                            <li></li>
                            <li>Mon</li>
                            <li></li>
                            <li>Wed</li>
                            <li></li>
                            <li>Fri</li>
                            <li></li>
                        </ul>
                        <ul class="heat-calendar__squares">
                        </ul>
                    </div>`;
    }

    protected renderSquares = async () => {
        if(this.loadActivityTask.status != TaskStatus.INITIAL) return;
        await this.loadActivityTask.run();
        // TODO: handle failure

        const activity = this.loadActivityTask.value!;
        const squares = this.querySelector('.heat-calendar__squares')!;
        const months = this.querySelector('.heat-calendar__months')!;
        const end = new Date();
        let curr = new Date(end.getFullYear(), end.getMonth(), end.getDate()-(52*7));
        // set to last sunday
        curr.setDate(curr.getDate() - curr.getDay());
        let lastMonthHeader = curr.getMonth();

        let spannedColumns = 1;
        let totalDays=0;

        while(curr.getTime() <= end.getTime()) {
            if(totalDays != 0 && totalDays % 7 == 0) {
                if(lastMonthHeader != curr.getMonth()) {
                    const monthAbbr:string = this.monthAbbreviations[lastMonthHeader+1];
                    
                    const el = document.createElement("li");
                    el.style.width = `calc(var(--week-width) * ${spannedColumns})`
                    if(spannedColumns > 2) {
                        el.innerHTML = monthAbbr;
                    }
                    months.appendChild(el);

                    lastMonthHeader = curr.getMonth();
                    spannedColumns=1;
                }else{
                    spannedColumns++;
                }
            }
            const paddedMonth = String(curr.getMonth()+1).padStart(2, '0');
            const paddedDate = String(curr.getDate()).padStart(2, '0');
            const squareActivity = activity[`${curr.getFullYear()}/${paddedMonth}/${paddedDate}`];
            console.log(`${curr.getFullYear()}/${paddedMonth}/${paddedDate}`)
            let backgroundColor = this.noActivityColor;
            if(squareActivity) {
                backgroundColor = this.colorSteps[Math.min(squareActivity, 3)]
            }
            squares.insertAdjacentHTML('beforeend', `<li class='${squareActivity ? 'active' : 'inactive'}' style="background-color:${backgroundColor}"></li>`);

            curr.setDate(curr.getDate()+1);
            totalDays++;
        }

        if(spannedColumns > 2) {
            const monthAbbr = this.monthAbbreviations[lastMonthHeader];
                    
            const el = document.createElement("li");
            el.style.width = `calc(var(--week-width) * ${spannedColumns})`
            if(spannedColumns > 2) {
                el.innerHTML = monthAbbr;
            }
            months.appendChild(el);
        }
    }
}
