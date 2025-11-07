document.getElementById("category").addEventListener("change", function () {
  	const selectedCategory = this.value;

	fetch(`/category=${encodeURIComponent(selectedCategory)}`)
	.then(response => response.text())
	.then(html => {
		const temp = document.createElement("div");
		temp.innerHTML = html;
		const newGrid = temp.querySelector("#product-grid");
		document.getElementById("product-grid").innerHTML = newGrid.innerHTML;
	});
});