var elementCheck = document.getElementById("#backgroundDivCheck");
var stylingValue = getComputedStyle(elementCheck);
var trueBackgroundValue = stylingValue.backgroundColor
console.log(trueBackgroundValue);
console.log(document.getElementById("prismLink"))
//

//rgb(255, 255, 254)
if (trueBackgroundValue == "rgb(15, 15, 15)") { // If media query matches
  document.getElementById("prismLink").setAttribute("href", "https://cdnjs.cloudflare.com/ajax/libs/prism/1.20.0/themes/prism-tomorrow.min.css");
  console.warn("SWAPPED THEME")
} else {
  y.setAttribute("href", "https://cdn.jsdelivr.net/npm/prismjs@1.20.0/themes/prism.css");
  console.error("THEME NOT CHANGED")
  console.error(x)
}
