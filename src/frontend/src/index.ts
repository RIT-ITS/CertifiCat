import "./styles/common.scss";
import "./components/stickyNav";
import "./components/mobileNav";
import "./components/profileMenu";
import "./components/newAccountFormManager";
import "./components/editableText";
import "./components/accountAccessManager";
import "./components/confirmButton";
import "./components/fadeOnLoad";

// adds label attribute to table data for responsive tables
document.querySelectorAll("table.collapsible").forEach((table) => {
  const thEls = table.querySelectorAll("thead th");
  const tdLabels = Array.from(thEls).map((el) => (el as HTMLElement).innerText);
  table.querySelectorAll("tbody tr").forEach((tr) => {
    Array.from(tr.children).forEach((td, ndx) =>
      td.setAttribute("label", tdLabels[ndx])
    );
  });
});
