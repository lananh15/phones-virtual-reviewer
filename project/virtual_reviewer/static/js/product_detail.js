// Converts URLs in the text into clickable links, optionally replacing them with titles from videoMap
function linkify(text, videoMap = {}) {
	const urlRegex = /https?:\/\/[^\s]+/g;
	
	return text.replace(urlRegex, function (rawUrl) {
		const cleanUrl = rawUrl.replace(/[.,;!?()\[\]]+$/, '');
		const title = videoMap[cleanUrl] || cleanUrl;
		const trailing = rawUrl.substring(cleanUrl.length);
		
		return `<a href="${cleanUrl}" target="_blank" class="text-blue-500 underline">${title}</a>${trailing}`;
	});
}

// Handles the "Generate Review" button click: fetches product review data, parses and displays it as formatted HTML with pros, cons, and links
document.getElementById("generateReviewBtn").addEventListener("click", async () => {
	const btn = document.getElementById("generateReviewBtn");
	const productName = btn.dataset.productName;

	btn.disabled = true;
	btn.innerHTML = `
		<svg class="animate-spin h-5 w-5 mr-2 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
			<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
			<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
		</svg>
		Đang tạo...
	`;
	btn.classList.add("animate-pulse", "cursor-wait", "opacity-80");

	try {
		const response = await fetch(`/tao-review/?name=${encodeURIComponent(productName)}`);
		const datas = await response.json();

		// console.log("📄 Toàn bộ reviews:");
		// console.log(datas.reviews);

		const parsedReviews = JSON.parse(datas.reviews);
		const reviewData = parsedReviews?.data?.[0];

		if (!reviewData) throw new Error("Không tìm thấy dữ liệu review phù hợp.");

		const data = {
			title: reviewData.title,
			intro: reviewData.intro,
			features: reviewData.features,
			pros: reviewData.pros,
			cons: reviewData.cons,
			suggestion: reviewData.suggestion,
		};
		const videoMap = datas.video_titles || {};

		const reviewHTML = `
		<div class="">
			<h2 class="uppercase text-2xl font-semibold text-blue-500 mb-4">${data.title}</h2>

			<section>
				<h3 class="text-xl font-semibold text-black-700 mb-1">Giới thiệu</h3>
				<p class="text-black-600">${linkify(data.intro, videoMap)}</p>
			</section>

			<section>
				<h3 class="text-xl font-semibold text-black-700 mt-4 mb-1">Tính năng nổi bật</h3>
				<p class="text-black-600">${linkify(data.features, videoMap)}</p>
			</section>

			<section class="mt-4">
				<h3 class="text-lg font-semibold text-black mb-2">Ưu và nhược điểm</h3>

				<table class="w-full border border-gray-300 border-collapse rounded">
					<thead>
						<tr class="bg-blue-100">
							<th class="px-4 py-2 font-bold text-black-700 border border-gray-300 text-left">Ưu điểm</th>
							<th class="px-4 py-2 font-bold text-black-700 border border-gray-300 text-left">Nhược điểm</th>
						</tr>
					</thead>

					<tbody>
					${(() => {
						const maxLength = Math.max(data.pros.length, data.cons.length);
						let rows = "";

						for (let i = 0; i < maxLength; i++) {
							rows += `
								<tr>
									<td class="px-4 py-2 text-black-700 border border-gray-300 align-top w-1/2">${linkify(data.pros[i] || "", videoMap)}</td>
									<td class="px-4 py-2 text-black-700 border border-gray-300 align-top">${linkify(data.cons[i] || "", videoMap)}</td>
								</tr>
							`;
						}

						return rows;
					})()}
					</tbody>
				</table>
			</section>

			<section class="mt-4">
				<h3 class="text-xl font-semibold text-black-700 mb-1">Gợi ý phù hợp cho những ai nên mua</h3>
				<p class="text-black-600">${linkify(data.suggestion, videoMap)}</p>
			</section>
		</div>
		`;

		document.getElementById("reviewContainer").innerHTML = reviewHTML;
	}
	catch (error) {
		document.getElementById("reviewContainer").innerHTML = `
		<p class="text-red-500">Cỗ máy rì viu đã gặp lỗi khi tạo review, vui lòng tải lại trang rồi tạo lại review nha</p>
		`;
	}
	finally {
		btn.disabled = false;
		btn.style.display = "none";
	}
});