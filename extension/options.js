const form = document.getElementById('options-form')
const warning = document.getElementById('warning')
const btn = form.querySelector('button')

form.addEventListener('submit', e => {
	/*
	Action associated with the 'save' button from the options menu
	Gathers objects, makes a JSON objects and store it under name 'server'
	*/
	e.preventDefault()
	const data = Array.prototype.reduce.call(form.elements, (obj, el) => {
		obj[el.name] = el.value
		return obj
	}, {})
	delete data['']
	
	browser.storage.local.set({server: data}).then(() => {
		btn.innerHTML = 'Saved!'
		setTimeout(() => {
			btn.innerHTML = 'Save'
		}, 600)
	})
})

/*
If the 'server' object does not already exist in browser storage, load it key by key
*/
browser.storage.local.get('server').then(({server}) => {
	if (!server) {
		return
	}
	for (const x of Object.keys(server)) {
		const el = form.querySelector('[name="' + x + '"]')
		if (el) {
			el.value = server[x]
		}
	}
})
