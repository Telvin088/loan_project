const loanAmount = document.getElementById("loan-amount");
const loanTenure = document.getElementById("loan-tenure");
const interestRate = document.getElementById("interest-rate");

const loanAmountValue = document.getElementById("loan-amount-value");
const loanTenureValue = document.getElementById("loan-tenure-value");
const interestRateValue = document.getElementById("interest-rate-value");

const emiResult = document.getElementById("emi-result");
const totalInterest = document.getElementById("total-interest");
const totalPayable = document.getElementById("total-payable");

function calculateEMI() {
  const principal = parseFloat(loanAmount.value);
  const months = parseInt(loanTenure.value);
  const rate = parseFloat(interestRate.value) / 100 / 12;

  const emi =
    (principal * rate * Math.pow(1 + rate, months)) /
    (Math.pow(1 + rate, months) - 1);
  const totalPayment = emi * months;
  const totalInterestPayable = totalPayment - principal;

  emiResult.textContent = `$${emi.toFixed(2)}`;
  totalInterest.textContent = `$${totalInterestPayable.toFixed(2)}`;
  totalPayable.textContent = `$${totalPayment.toFixed(2)}`;
}

loanAmount.addEventListener("input", () => {
  loanAmountValue.textContent = `$${loanAmount.value}`;
  calculateEMI();
});

loanTenure.addEventListener("input", () => {
  loanTenureValue.textContent = `${loanTenure.value} months`;
  calculateEMI();
});

interestRate.addEventListener("input", () => {
  interestRateValue.textContent = `${interestRate.value}%`;
  calculateEMI();
});

calculateEMI();

// faq js
var acc = document.getElementsByClassName("accordion");

for (var i = 0; i < acc.length; i++) {
  acc[i].addEventListener("click", function () {
    for (var j = 0; j < acc.length; j++) {
      var panel = acc[j].nextElementSibling;
      if (acc[j] !== this) {
        acc[j].classList.remove("active");
        panel.style.height = null;
        panel.style.paddingTop = null;
        panel.style.paddingBottom = null;
      }
    }
    this.classList.toggle("active");
    var panel = this.nextElementSibling;
    if (panel.style.height) {
      panel.style.height = null;
      panel.style.paddingTop = null;
      panel.style.paddingBottom = null;
    } else {
      var panelContent = panel.querySelector(".panel-content");
      panel.style.height = panelContent.scrollHeight + "px";
      panel.style.paddingTop = "18px";
      panel.style.paddingBottom = "18px";
    }
  });
}
