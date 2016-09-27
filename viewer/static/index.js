/*!
 * chameleon-crawler
 *
 * Copyright 2016 ghostwords.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 *
 */

function init_checkboxes() {
	var els = document.querySelectorAll('.select-all');

	function find_parent(el) {
		var parent = el;
		while (['table', 'form'].indexOf(parent.tagName.toLowerCase()) == -1) {
			parent = parent.parentNode;
		}
		return parent;
	}

	for (var i = 0, count = els.length; i < count; i++) {
		var child_checks = find_parent(els[i])
			.querySelectorAll('input[type=checkbox]');

		(function (checks) {
			els[i].addEventListener('click', function () {
				for (var i = 0, count = checks.length; i < count; i++) {
					if (checks[i] != this) {
						checks[i].checked = this.checked;
					}
				}
			});
		}(child_checks));
	}
}

document.addEventListener('DOMContentLoaded', function () {
	init_checkboxes();
});
