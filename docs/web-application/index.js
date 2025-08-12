const rosas = {};

document.addEventListener("DOMContentLoaded", () => {
	document.body.insertAdjacentHTML("beforeend", `<div class="theme-toggle" id="theme-toggle"></div>`);
	let isCurrentThemeDark = false;
	rosas.themeToggle = document.getElementById("theme-toggle");
	rosas.themeToggle.onclick = () => {
		if (isCurrentThemeDark) {
			document.documentElement.style.setProperty("--color", "#222");
			document.documentElement.style.setProperty("--background-color", "#FFF");
		}
		else {
			document.documentElement.style.setProperty("--color", "#EEE");
			document.documentElement.style.setProperty("--background-color", "#111");
		}
		isCurrentThemeDark = !isCurrentThemeDark;
	};

	document.body.insertAdjacentHTML("beforeend", `<div class="toast hidden-toast" id="toast-display"><span id="toast-text-span"></span><div class="toast-close-button" id="toast-close-button">×</div></div>`);
	rosas.toastDisplay = document.getElementById("toast-display");
	rosas.toastTextSpan = document.getElementById("toast-text-span");
	rosas.toastCloseButton = document.getElementById("toast-close-button");
	rosas.toastCloseButton.addEventListener("click", () => {
		rosas.toastDisplay.classList = "toast hidden-toast";
		clearTimeout(rosas.toastFadeOutTimerId);
	});
});

function toast(message, status = "default") {
	rosas.toastDisplay.classList = `toast ${status}-toast`;
	rosas.toastTextSpan.textContent = message;
	clearTimeout(rosas.toastFadeOutTimerId);
	rosas.toastFadeOutTimerId = setTimeout(() => {
		rosas.toastDisplay.classList = "toast hidden-toast";
	}, 4000);
}
function showInformationToast(message) { toast(message, "information"); }
function showSuccessToast(message) { toast(message, "success"); }
function showWarningToast(message) { toast(message, "warning"); }
function showErrorToast(message) { toast(message, "error"); }
