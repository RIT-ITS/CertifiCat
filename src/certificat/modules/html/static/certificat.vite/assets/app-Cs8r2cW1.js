import{t as c,b as h,n as l,e as w,c as Nt,x as o,d as p,f as A,h as $t,s as y,g as ae,i as ie,H as Ft,j as ne,C as oe}from"./vendor-CJI7RD2x.js";var le=Object.getOwnPropertyDescriptor,de=(t,e,s,a)=>{for(var r=a>1?void 0:a?le(e,s):e,i=t.length-1,n;i>=0;i--)(n=t[i])&&(r=n(r)||r);return r};let Lt=class extends h{constructor(){super(...arguments),this.topPadding=0,this.onScroll=()=>{this.topPadding<window.scrollY?this.classList.add("is-sticky"):this.classList.remove("is-sticky")}}createRenderRoot(){return this}connectedCallback(){this.topPadding=parseFloat(window.getComputedStyle(this).paddingTop),window.addEventListener("scroll",this.onScroll),super.connectedCallback(),this.onScroll()}};Lt=de([c("sticky-nav")],Lt);var ce=Object.defineProperty,he=Object.getOwnPropertyDescriptor,Ut=t=>{throw TypeError(t)},Bt=(t,e,s,a)=>{for(var r=a>1?void 0:a?he(e,s):e,i=t.length-1,n;i>=0;i--)(n=t[i])&&(r=(a?n(e,s,r):n(r))||r);return a&&r&&ce(e,s,r),r},qt=(t,e,s)=>e.has(t)||Ut("Cannot "+s),pe=(t,e,s)=>(qt(t,e,"read from private field"),s?s.call(t):e.get(t)),ue=(t,e,s)=>e.has(t)?Ut("Cannot add the same private member more than once"):e instanceof WeakSet?e.add(t):e.set(t,s),ve=(t,e,s,a)=>(qt(t,e,"write to private field"),e.set(t,s),s),F;let Et=class extends h{constructor(){super(...arguments),ue(this,F),this.show=()=>{this.classList.remove("mobile-menu--hidden")},this.hide=()=>{this.classList.add("mobile-menu--hidden")}}get trigger(){return pe(this,F)}set trigger(t){ve(this,F,t)}createRenderRoot(){return this}connectedCallback(){super.connectedCallback(),this.triggerEl=document.querySelector(this.trigger),this.triggerEl.addEventListener("click",this.show),this.closeLink.addEventListener("click",this.hide),this.querySelector(".overlay")?.addEventListener("click",this.hide)}};F=new WeakMap;Bt([l()],Et.prototype,"trigger",1);Bt([w("#close-mobile-navigation-link")],Et.prototype,"closeLink",2);Et=Bt([c("mobile-nav")],Et);var ge=Object.defineProperty,ye=Object.getOwnPropertyDescriptor,Dt=(t,e,s,a)=>{for(var r=a>1?void 0:a?ye(e,s):e,i=t.length-1,n;i>=0;i--)(n=t[i])&&(r=(a?n(e,s,r):n(r))||r);return a&&r&&ge(e,s,r),r};let Tt=class extends h{constructor(){super(...arguments),this.toggle=t=>{this.classList.contains("profile--show")?this.classList.remove("profile--show"):this.classList.add("profile--show"),t.stopPropagation()},this.submenuClick=t=>{t.stopPropagation()},this.hide=()=>{this.classList.remove("profile--show")}}createRenderRoot(){return this}connectedCallback(){super.connectedCallback(),this.submenuToggle.addEventListener("mousedown",this.toggle),this.submenu.addEventListener("mousedown",this.submenuClick),document.addEventListener("mousedown",this.hide),document.addEventListener("scroll",this.hide)}};Dt([w(".submenu-toggle")],Tt.prototype,"submenuToggle",2);Dt([w(".submenu")],Tt.prototype,"submenu",2);Tt=Dt([c("profile-menu")],Tt);var fe=Object.defineProperty,_e=Object.getOwnPropertyDescriptor,O=(t,e,s,a)=>{for(var r=a>1?void 0:a?_e(e,s):e,i=t.length-1,n;i>=0;i--)(n=t[i])&&(r=(a?n(e,s,r):n(r))||r);return a&&r&&fe(e,s,r),r};let C=class extends h{constructor(){super(),this.setGroupVisibility=()=>{this.group.style.display=this.groupScope?.checked?"block":"none",this.groupLabel.style.display=this.groupScope?.checked?"block":"none"}}connectedCallback(){super.connectedCallback(),this.setupEvents(),this.setGroupVisibility()}setupEvents(){this.scopes.forEach(t=>t.addEventListener("change",this.setGroupVisibility))}createRenderRoot(){return this}render(){return o` ${this.children} `}};O([w("form")],C.prototype,"form",2);O([w("#id_scope_1")],C.prototype,"groupScope",2);O([w("#id_group")],C.prototype,"group",2);O([w("label[for=id_group]")],C.prototype,"groupLabel",2);O([Nt("[name=scope]")],C.prototype,"scopes",2);C=O([c("new-account-form-manager")],C);var me=Object.defineProperty,we=Object.getOwnPropertyDescriptor,Yt=t=>{throw TypeError(t)},k=(t,e,s,a)=>{for(var r=a>1?void 0:a?we(e,s):e,i=t.length-1,n;i>=0;i--)(n=t[i])&&(r=(a?n(e,s,r):n(r))||r);return a&&r&&me(e,s,r),r},Jt=(t,e,s)=>e.has(t)||Yt("Cannot "+s),$=(t,e,s)=>(Jt(t,e,"read from private field"),s?s.call(t):e.get(t)),E=(t,e,s)=>e.has(t)?Yt("Cannot add the same private member more than once"):e instanceof WeakSet?e.add(t):e.set(t,s),T=(t,e,s,a)=>(Jt(t,e,"write to private field"),e.set(t,s),s),U,q,Y,J,V,j,z,K;let m=class extends h{constructor(){super(...arguments),E(this,U,"Edit"),E(this,q,"button"),E(this,Y,"button"),E(this,J),E(this,V,!1),E(this,j,new Map),E(this,z,!1),E(this,K),this.transitionToEdit=()=>{this.classList.add("editing"),this.editMode=!0,this.editableElements().forEach((t,e)=>{this.contentBeforeEditing.set(e,t.innerHTML||"");try{t.contentEditable="plaintext-only"}catch{t.contentEditable="true"}t.focus()})},this.cancelEdit=()=>{this.editableElements().forEach((t,e)=>{t.innerHTML=this.contentBeforeEditing.get(e)}),this.transitionToReadonly()},this.transitionToReadonly=()=>{this.classList.remove("editing"),this.editMode=!1,this.editableElements().forEach(t=>{t.contentEditable="false"})},this.save=async()=>{if(this.saving)return;this.saving=!0;var t={};this.editableElements().forEach((s,a)=>{s.contentEditable="false",t[a]=s.innerText=s.innerText.trim()});let e=!1;try{e=(await fetch(this.url,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(t),credentials:"same-origin"})).status!==200}catch{e=!0}this.saving=!1,e?(this.editableElements().forEach(s=>{try{s.contentEditable="plaintext-only"}catch{s.contentEditable="true"}}),alert("There was an error saving")):this.transitionToReadonly()}}get editButtonText(){return $(this,U)}set editButtonText(t){T(this,U,t)}get editButtonDisplay(){return $(this,q)}set editButtonDisplay(t){T(this,q,t)}get actionButtonDisplay(){return $(this,Y)}set actionButtonDisplay(t){T(this,Y,t)}get url(){return $(this,J)}set url(t){T(this,J,t)}get editMode(){return $(this,V)}set editMode(t){T(this,V,t)}get contentBeforeEditing(){return $(this,j)}set contentBeforeEditing(t){T(this,j,t)}get saving(){return $(this,z)}set saving(t){T(this,z,t)}get editableWrap(){return $(this,K)}set editableWrap(t){T(this,K,t)}createRenderRoot(){return this}editableElements(){var t=new Map;return this.querySelectorAll(".edit-wrap>[data-editable-id]").forEach(e=>{t.set(e.getAttribute("data-editable-id"),e)}),t}connectedCallback(){for(super.connectedCallback(),this.editableWrap=document.createElement("div"),this.editableWrap.classList.add("edit-wrap");this.childNodes.length>0;)this.editableWrap.appendChild(this.childNodes[0]);this.replaceChildren(this.editableWrap)}render(){return o` <div class="buttons">${this.renderButtons()}</div> `}renderButtons(){if(this.editMode){const t={cancel:!0,btn:this.actionButtonDisplay=="button","btn-light":this.actionButtonDisplay=="button","btn-sm":this.actionButtonDisplay=="button"},e={save:!0,btn:this.actionButtonDisplay=="button","btn-primary":this.actionButtonDisplay=="button","btn-sm":this.actionButtonDisplay=="button"};return o`
                <a
                    href="javascript:return false;"
                    ?disabled="${this.saving}"
                    class="${A(t)}"
                    @click="${this.cancelEdit}"
                >
                    Cancel &nbsp;<span class="fa-solid fa-backward"></span>
                </a>
                <a
                    href="javascript:return false;"
                    ?disabled="${this.saving}"
                    class="${A(e)}"
                    @click="${this.save}"
                >
                    Save &nbsp;<span class="fa-solid fa-floppy-disk"></span>
                </a>
            `}else{const t={btn:this.editButtonDisplay=="button","btn-primary":this.editButtonDisplay=="button","btn-sm":this.editButtonDisplay=="button"};return o`
                <a
                    href="javascript:return false;"
                    class="${A(t)}"
                    @click="${this.transitionToEdit}"
                >
                    ${this.editButtonText} &nbsp;<span class="fa-regular fa-pen-to-square"></span>
                </a>
            `}}};U=new WeakMap;q=new WeakMap;Y=new WeakMap;J=new WeakMap;V=new WeakMap;j=new WeakMap;z=new WeakMap;K=new WeakMap;k([l()],m.prototype,"editButtonText",1);k([l()],m.prototype,"editButtonDisplay",1);k([l()],m.prototype,"actionButtonDisplay",1);k([l()],m.prototype,"url",1);k([p()],m.prototype,"editMode",1);k([p()],m.prototype,"contentBeforeEditing",1);k([p()],m.prototype,"saving",1);m=k([c("editable-text")],m);function be(t){return t instanceof Error?t.message:String(t)}var $e=Object.defineProperty,Ee=Object.getOwnPropertyDescriptor,Vt=t=>{throw TypeError(t)},_=(t,e,s,a)=>{for(var r=a>1?void 0:a?Ee(e,s):e,i=t.length-1,n;i>=0;i--)(n=t[i])&&(r=(a?n(e,s,r):n(r))||r);return a&&r&&$e(e,s,r),r},jt=(t,e,s)=>e.has(t)||Vt("Cannot "+s),u=(t,e,s)=>(jt(t,e,"read from private field"),s?s.call(t):e.get(t)),v=(t,e,s)=>e.has(t)?Vt("Cannot add the same private member more than once"):e instanceof WeakSet?e.add(t):e.set(t,s),g=(t,e,s,a)=>(jt(t,e,"write to private field"),e.set(t,s),s),Q,X,Z,tt,et,st,rt,at,it,nt;let d=class extends h{constructor(){super(...arguments),v(this,Q),v(this,X),v(this,Z),v(this,tt,!1),v(this,et,!1),v(this,st,!1),v(this,rt,null),v(this,at,new $t(this,{autoRun:!1,task:async()=>{const t=await fetch(this.groupFetchUrl,{method:"GET",credentials:"same-origin"});if(t.status!==200)throw new Error(`${t.status} status code returned from endpoint`);try{return await t.json()}catch{throw new Error("Unexpected result returned from endpoint")}}})),v(this,it,new $t(this,{autoRun:!1,task:async t=>{const[e,s]=t,a=this.loadGroupsTask.value.find(n=>n.id==s);if(!a)throw Error("You're not allowed to remove that group.");const r=Array.from(this.accessibleBy).find(n=>n.id==s);if(e=="add"&&r)return;const i=await fetch(this.groupUpdateUrl,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({groups:{[e]:[s]}}),credentials:"same-origin"});if(i.status!==200)throw new Error(`${i.status} status code returned from endpoint`);e=="add"?this.accessibleBy=this.accessibleBy.add(a):(this.accessibleBy.delete(r),this.accessibleBy=new Set(this.accessibleBy))}})),v(this,nt),this.transitionToEdit=async()=>{if(!this.editMode){this.editMode=!0;try{await this.loadGroupsTask.run()}catch(t){this.error=be(t),this.editMode=!1}}},this.transitionToReadonly=()=>{this.editMode=!1},this.addGroup=t=>{this.modifyGroupsTask.run(["add",t])},this.removeGroup=t=>{this.modifyGroupsTask.run(["del",t])}}get groupFetchUrl(){return u(this,Q)}set groupFetchUrl(t){g(this,Q,t)}get groupUpdateUrl(){return u(this,X)}set groupUpdateUrl(t){g(this,X,t)}get accessibleBy(){return u(this,Z)}set accessibleBy(t){g(this,Z,t)}get clientIsOwner(){return u(this,tt)}set clientIsOwner(t){g(this,tt,t)}get editMode(){return u(this,et)}set editMode(t){g(this,et,t)}get saving(){return u(this,st)}set saving(t){g(this,st,t)}get error(){return u(this,rt)}set error(t){g(this,rt,t)}get loadGroupsTask(){return u(this,at)}set loadGroupsTask(t){g(this,at,t)}get modifyGroupsTask(){return u(this,it)}set modifyGroupsTask(t){g(this,it,t)}get editableWrap(){return u(this,nt)}set editableWrap(t){g(this,nt,t)}createRenderRoot(){return this}connectedCallback(){super.connectedCallback(),this.accessibleBy=new Set(this.accessibleBy)}render(){return o`
            ${this.renderError()}
            <div class="flex">
                ${this.renderHeader()}
                ${this.renderEditButton()}
                ${this.renderCancelButton()}
            </div>
            ${this.editMode?this.loadGroupsTask.render({complete:t=>t.length>0?o`
                                ${this.clientIsOwner?null:o`<div class='messages messages--info messages-small mb-2'>You are not the owner of this account. If you edit groups you could remove your access to this resource.</div>`}
                                ${this.renderGroupDisplay()}
                                ${this.renderAdd()}
                            `:o`<b class='bold'>You're not in any groups</b>`}):this.renderGroupDisplay()}
        `}renderError(){const t=this.loadGroupsTask.error??this.modifyGroupsTask.error;return t?o`<div class='messages messages--error messages-small mb-2'>${t.message}</div>`:null}renderHeader(){return o`<div class="accessmanager--header">${this.accessibleBy.size>0?"Owner & Group Membership":"Owner Only"}</div>`}renderGroupDisplay(){return o`
            <ul>
            ${Array.from(this.accessibleBy).map(t=>o`<li>
                                <span class="mr-2"><i class="fa-solid fa-user-group"></i></span>
                                <span class="accessmanager--groupname">${t.name}</span>
                                ${this.editMode?o`<a
                                    href="javascript:return false;"
                                    class="accessmanager--edit"
                                    @click="${()=>this.removeGroup(t.id)}"
                                >
                                   &nbsp;<span class="fa-solid fa-trash fa-lg"></span>
                                </a>`:null}
                            </li>`)}
            </ul>
        `}canRemove(t){return!!this.loadGroupsTask.value.find(e=>e.id==t.id)}renderEditButton(){return this.editMode?null:o`<a
                    href="javascript:return false;"
                    class="accessmanager--edit"
                    @click="${this.transitionToEdit}"
                >
                    Edit &nbsp;<span class="fa-regular fa-pen-to-square"></span>
                </a>`}renderCancelButton(){return this.editMode?o`<a
                    href="javascript:return false;"
                    class="accessmanager--cancel"
                    @click="${this.transitionToReadonly}"
                >
                    Stop Editing &nbsp;<span class="fa-solid fa-backward"></span>
                </a>`:null}renderAdd(){if(!this.editMode||this.loadGroupsTask.status!=y.COMPLETE)return null;const t=ie();return o`<div class="accessmanager--add">
                        <select ${ae(t)}>
                            ${this.loadGroupsTask.value.map(e=>o`
                                <option value="${e.id}">${e.name}</option>
                            `)}
                        </select>
                        <a @click="${()=>this.addGroup(Number(t.value.value))}" class="btn btn--primary-outline btn--sm">Add</a>
                    </div>`}};Q=new WeakMap;X=new WeakMap;Z=new WeakMap;tt=new WeakMap;et=new WeakMap;st=new WeakMap;rt=new WeakMap;at=new WeakMap;it=new WeakMap;nt=new WeakMap;_([l()],d.prototype,"groupFetchUrl",1);_([l()],d.prototype,"groupUpdateUrl",1);_([l({type:Array})],d.prototype,"accessibleBy",1);_([l({type:Boolean})],d.prototype,"clientIsOwner",1);_([p()],d.prototype,"editMode",1);_([p()],d.prototype,"saving",1);_([p()],d.prototype,"error",1);_([p()],d.prototype,"loadGroupsTask",1);_([p()],d.prototype,"modifyGroupsTask",1);d=_([c("account-access-manager")],d);var Te=Object.defineProperty,ke=Object.getOwnPropertyDescriptor,zt=t=>{throw TypeError(t)},S=(t,e,s,a)=>{for(var r=a>1?void 0:a?ke(e,s):e,i=t.length-1,n;i>=0;i--)(n=t[i])&&(r=(a?n(e,s,r):n(r))||r);return a&&r&&Te(e,s,r),r},Kt=(t,e,s)=>e.has(t)||zt("Cannot "+s),x=(t,e,s)=>(Kt(t,e,"read from private field"),s?s.call(t):e.get(t)),R=(t,e,s)=>e.has(t)?zt("Cannot add the same private member more than once"):e instanceof WeakSet?e.add(t):e.set(t,s),G=(t,e,s,a)=>(Kt(t,e,"write to private field"),e.set(t,s),s),ot,lt,dt,ct;let M=class extends h{constructor(){super(...arguments),this.showWarning=!1,R(this,ot),R(this,lt),R(this,dt),R(this,ct)}get warningText(){return x(this,ot)}set warningText(t){G(this,ot,t)}get value(){return x(this,lt)}set value(t){G(this,lt,t)}get name(){return x(this,dt)}set name(t){G(this,dt,t)}get buttonType(){return x(this,ct)}set buttonType(t){G(this,ct,t)}createRenderRoot(){return this}render(){return this.showWarning?o`
                <p>${this.warningText}</p>
                <input
                    @click=${()=>this.showWarning=!1}
                    type="button"
                    value="Cancel" 
                    class="btn btn--secondary btn--primary" />
                <input
                    .name="${this.name}" 
                    .type="${this.buttonType||"button"}"
                    .value="${this.value}" 
                    class="btn btn--primary btn--danger" />
            `:o`
                <input
                    @click=${()=>this.showWarning=!0}
                    type="button"
                    .value="${this.value}" 
                    class="btn btn--primary btn--danger" />
            `}};ot=new WeakMap;lt=new WeakMap;dt=new WeakMap;ct=new WeakMap;S([p()],M.prototype,"showWarning",2);S([l()],M.prototype,"warningText",1);S([l()],M.prototype,"value",1);S([l()],M.prototype,"name",1);S([l()],M.prototype,"buttonType",1);M=S([c("confirm-button")],M);var Ce=Object.getOwnPropertyDescriptor,Me=(t,e,s,a)=>{for(var r=a>1?void 0:a?Ce(e,s):e,i=t.length-1,n;i>=0;i--)(n=t[i])&&(r=n(r)||r);return r};let xt=class extends h{createRenderRoot(){return this}connectedCallback(){super.connectedCallback(),this.classList.add("loaded")}};xt=Me([c("fade-on-load")],xt);function Oe(t,e,s){s=Math.max(Math.min(s,1),0);const a=Rt(t),r=Rt(e),i={r:Math.round(a.r*(1-s)+r.r*s),g:Math.round(a.g*(1-s)+r.g*s),b:Math.round(a.b*(1-s)+r.b*s)};return Se(i)}function Rt(t){t=t.replace("#","");const e=parseInt(t.substring(0,2),16),s=parseInt(t.substring(2,4),16),a=parseInt(t.substring(4,6),16);return{r:e,g:s,b:a}}function Se(t){const e=t.r.toString(16).padStart(2,"0"),s=t.g.toString(16).padStart(2,"0"),a=t.b.toString(16).padStart(2,"0");return"#"+e+s+a}var Pe=Object.defineProperty,Be=Object.getOwnPropertyDescriptor,Qt=t=>{throw TypeError(t)},Ct=(t,e,s,a)=>{for(var r=a>1?void 0:a?Be(e,s):e,i=t.length-1,n;i>=0;i--)(n=t[i])&&(r=(a?n(e,s,r):n(r))||r);return a&&r&&Pe(e,s,r),r},Xt=(t,e,s)=>e.has(t)||Qt("Cannot "+s),H=(t,e,s)=>(Xt(t,e,"read from private field"),s?s.call(t):e.get(t)),I=(t,e,s)=>e.has(t)?Qt("Cannot add the same private member more than once"):e instanceof WeakSet?e.add(t):e.set(t,s),N=(t,e,s,a)=>(Xt(t,e,"write to private field"),e.set(t,s),s),ht,pt,ut,vt;let L=class extends h{constructor(){super(...arguments),I(this,ht),I(this,pt),I(this,ut,[]),I(this,vt,new $t(this,{autoRun:!1,task:async()=>{const t=await fetch(this.url,{method:"GET",credentials:"same-origin"});if(t.status!==200)throw new Error(`${t.status} status code returned from endpoint`);try{return await t.json()}catch{throw new Error("Unexpected result returned from endpoint")}}})),this.monthAbbreviations={0:"Jan",1:"Feb",2:"Mar",3:"Apr",4:"May",5:"Jun",6:"Jul",7:"Aug",8:"Sep",9:"Oct",10:"Nov",11:"Dec"},this.renderSquares=async()=>{if(this.loadActivityTask.status!=y.INITIAL)return;await this.loadActivityTask.run();const t=this.loadActivityTask.value,e=this.querySelector(".heat-calendar__squares"),s=this.querySelector(".heat-calendar__months"),a=new Date;let r=new Date(a.getFullYear(),a.getMonth(),a.getDate()-364);r.setDate(r.getDate()-r.getDay());let i=r.getMonth(),n=1,Mt=0;for(;r.getTime()<=a.getTime();){if(Mt!=0&&Mt%7==0)if(i!=r.getMonth()){const re=this.monthAbbreviations[i],Pt=document.createElement("li");Pt.style.width=`calc(var(--week-width) * ${n})`,n>2&&(Pt.innerHTML=re),s.appendChild(Pt),i=r.getMonth(),n=1}else n++;const Ot=String(r.getMonth()+1).padStart(2,"0"),P=String(r.getDate()).padStart(2,"0"),St=t[`${r.getFullYear()}/${Ot}/${P}`];let At=this.noActivityColor;St&&(At=this.colorSteps[Math.min(St,3)]),e.insertAdjacentHTML("beforeend",`<li class='${St?"active":"inactive"}' style="background-color:${At}"></li>`),r.setDate(r.getDate()+1),Mt++}if(n>2){const Ot=this.monthAbbreviations[i],P=document.createElement("li");P.style.width=`calc(var(--week-width) * ${n})`,n>2&&(P.innerHTML=Ot),s.appendChild(P)}}}get url(){return H(this,ht)}set url(t){N(this,ht,t)}get noActivityColor(){return H(this,pt)}set noActivityColor(t){N(this,pt,t)}get colorSteps(){return H(this,ut)}set colorSteps(t){N(this,ut,t)}get loadActivityTask(){return H(this,vt)}set loadActivityTask(t){N(this,vt,t)}daysInMonth(t){return new Date(t.getFullYear(),t.getMonth()+1,0).getDate()}connectedCallback(){super.connectedCallback();const t=window.getComputedStyle(this).getPropertyValue("--heat-calendar--start-color"),e=window.getComputedStyle(this).getPropertyValue("--heat-calendar--end-color");for(let s=1;s<=3;s++)this.colorSteps[s]=Oe(t,e,(s-1)/2)}createRenderRoot(){return this}render(){window.requestAnimationFrame(this.renderSquares);const t={"heat-calendar":!0,loading:this.loadActivityTask.status!=y.COMPLETE,error:this.loadActivityTask.status==y.ERROR};return o`<div class="${A(t)}">
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
                    </div>`}};ht=new WeakMap;pt=new WeakMap;ut=new WeakMap;vt=new WeakMap;Ct([l()],L.prototype,"url",1);Ct([l()],L.prototype,"noActivityColor",1);Ct([p()],L.prototype,"loadActivityTask",1);L=Ct([c("activity-graph")],L);var De=Object.defineProperty,We=Object.getOwnPropertyDescriptor,Zt=t=>{throw TypeError(t)},Wt=(t,e,s,a)=>{for(var r=a>1?void 0:a?We(e,s):e,i=t.length-1,n;i>=0;i--)(n=t[i])&&(r=(a?n(e,s,r):n(r))||r);return a&&r&&De(e,s,r),r},te=(t,e,s)=>e.has(t)||Zt("Cannot "+s),Gt=(t,e,s)=>(te(t,e,"read from private field"),s?s.call(t):e.get(t)),Ht=(t,e,s)=>e.has(t)?Zt("Cannot add the same private member more than once"):e instanceof WeakSet?e.add(t):e.set(t,s),It=(t,e,s,a)=>(te(t,e,"write to private field"),e.set(t,s),s),gt,yt;const Ae=t=>new Promise(e=>setTimeout(e,t));let kt=class extends h{constructor(){super(...arguments),Ht(this,gt),Ht(this,yt,new $t(this,{autoRun:!1,task:async()=>{const[t,e]=await Promise.all([fetch(this.url,{method:"GET",credentials:"same-origin"}),Ae(1e3)]);if(t.status!==200)throw new Error(`${t.status} status code returned from endpoint`);try{return await t.json()}catch{throw new Error("Unexpected result returned from endpoint")}}})),this.renderHistoryEvents=()=>{let t=this.loadHistoryTask.value;if(t)return o`
                <div class="history--tablewrap">
                    <table class="table table--light">
                        <thead class="thead--light">
                            <tr>
                                <th>Event Time</th>
                                <th>Resource</th>
                                <th>Description</th>
                                <th>Payload</th>
                            </tr>
                        </thead>
                        
                        ${t.events.map(e=>this.renderEventRow(t,e))}
                    </table>
                </div>`;switch(this.loadHistoryTask.status){case y.INITIAL:return o`<div>History hasn't been loaded. Refresh the history to see events.`;case y.PENDING:return o`<div>Loading history...</div>`;case y.ERROR:return o`<div>There was an error loading history.`}return null},this.renderEventRow=(t,e)=>o`
        <tr>
            <td class="shrink-cell">${new Date(e.created_at).toISOString()}</td>
            <td class="shrink-cell">${this.renderAssociatedObject(t,e)}</td>
            <td>${e.event_type_display}</td>
            <td>${this.renderPayload(e.payload)}</td>
        </tr>`,this.renderAssociatedObject=(t,e)=>{try{return t.sources[e.source.content_type][e.source.object_id].repr}catch{return o`<i>repr not found</i>`}},this.renderPayload=t=>t?Object.entries(t).map(([e,s])=>o`
                    ${e}: ${s} <br />
                `):null,this.renderHistory=async()=>{this.loadHistoryTask.status!=y.INITIAL},this.reload=()=>{this.loadHistoryTask.status!=y.PENDING&&this.loadHistoryTask.run()}}get url(){return Gt(this,gt)}set url(t){It(this,gt,t)}get loadHistoryTask(){return Gt(this,yt)}set loadHistoryTask(t){It(this,yt,t)}createRenderRoot(){return this}connectedCallback(){super.connectedCallback()}render(){const t={"fa-solid":!0,"fa-refresh":!0,"refresh-button":!0,"fa-spin":this.loadHistoryTask.status==y.PENDING};return o`
        <h4 class='icon'><i class="fa-solid fa-clock"></i>
            Event History
            <i class="${A(t)}" @click="${this.reload}"></i>
        </h4>
        ${this.renderHistoryEvents()}
        `}};gt=new WeakMap;yt=new WeakMap;Wt([l()],kt.prototype,"url",1);Wt([p()],kt.prototype,"loadHistoryTask",1);kt=Wt([c("order-history")],kt);var Le=Object.defineProperty,xe=Object.getOwnPropertyDescriptor,ee=t=>{throw TypeError(t)},b=(t,e,s,a)=>{for(var r=a>1?void 0:a?xe(e,s):e,i=t.length-1,n;i>=0;i--)(n=t[i])&&(r=(a?n(e,s,r):n(r))||r);return a&&r&&Le(e,s,r),r},se=(t,e,s)=>e.has(t)||ee("Cannot "+s),B=(t,e,s)=>(se(t,e,"read from private field"),s?s.call(t):e.get(t)),D=(t,e,s)=>e.has(t)?ee("Cannot add the same private member more than once"):e instanceof WeakSet?e.add(t):e.set(t,s),W=(t,e,s,a)=>(se(t,e,"write to private field"),e.set(t,s),s),ft,_t,mt,wt,bt;let f=class extends h{constructor(){super(),D(this,ft),D(this,_t),D(this,mt),D(this,wt),D(this,bt),this.show=()=>{this.modal.classList.add("modal--shown"),this.autoFocus&&this.querySelector(this.autoFocus)?.focus()},this.hide=()=>{this.modal.classList.remove("modal--shown")}}get trigger(){return B(this,ft)}set trigger(t){W(this,ft,t)}get header(){return B(this,_t)}set header(t){W(this,_t,t)}get addButtonText(){return B(this,mt)}set addButtonText(t){W(this,mt,t)}get addButtonName(){return B(this,wt)}set addButtonName(t){W(this,wt,t)}get autoFocus(){return B(this,bt)}set autoFocus(t){W(this,bt,t)}connectedCallback(){super.connectedCallback(),this.triggerEl=document.querySelector(this.trigger),this.triggerEl.addEventListener("click",this.show)}firstUpdated(t){super.firstUpdated(t),this.closeLinks.forEach(e=>e.addEventListener("click",this.hide)),this.modalContent.addEventListener("click",e=>(e.stopPropagation(),!1))}createRenderRoot(){return this}render(){return o`
            <form action="." method="post">
                <div class="modal">
                    <div class="modal--container modal-close">
                        <div class="modal--content">
                            <div class="modal--header modal--header--custom px-3 py-3">
                                <h3 class="bold mb-0">${this.header}</h3>
                                <a class="btn btn--light btn--md bg-gray-500 modal-close"><i class="fa-solid fa-close"></i></a>
                            </div>
                            <div class="modal--body px-3 py-3">
                                ${this.children}
                            </div>
                            <div class="modal--footer px-3 py-3">
                                <div class="modal--footer--custom">
                                    <div class="modal--footer--buttons rtl-buttons">
                                        <input 
                                            class="btn btn--primary btn--md" 
                                            type="submit"
                                            name="${this.addButtonName}" 
                                            value="${this.addButtonText}" />
                                        <a class="btn btn--primary btn--md btn--primary-outline modal-cancel modal-close">Cancel</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </form>
        `}};ft=new WeakMap;_t=new WeakMap;mt=new WeakMap;wt=new WeakMap;bt=new WeakMap;b([l()],f.prototype,"trigger",1);b([l()],f.prototype,"header",1);b([l()],f.prototype,"addButtonText",1);b([l()],f.prototype,"addButtonName",1);b([l()],f.prototype,"autoFocus",1);b([w(".modal")],f.prototype,"modal",2);b([w(".modal--content")],f.prototype,"modalContent",2);b([Nt(".modal-close")],f.prototype,"closeLinks",2);f=b([c("form-modal")],f);Ft.registerLanguage("bash",ne);window.hljs=Ft;window.hljsCopyPlugin=oe;document.querySelectorAll("table.collapsible").forEach(t=>{const e=t.querySelectorAll("thead th"),s=Array.from(e).map(a=>a.innerText);t.querySelectorAll("tbody tr").forEach(a=>{Array.from(a.children).forEach((r,i)=>{r.getAttribute("label")||r.setAttribute("label",s[i])})})});
