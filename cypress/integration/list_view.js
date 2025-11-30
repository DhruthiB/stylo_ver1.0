context("List View", () => {
	before(() => {
		cy.login();
		cy.visit("/app/website");
		return cy
			.window()
			.its("stylo")
			.then((stylo) => {
				return stylo.xcall("stylo.tests.ui_test_helpers.setup_workflow");
			});
	});

	it('enables "Actions" button', { scrollBehavior: false }, () => {
		const actions = [
			"Approve",
			"Reject",
			"Export",
			"Assign To",
			"Apply Assignment Rule",
			"Add Tags",
			"Print",
		];
		cy.go_to_list("ToDo");
		cy.clear_filters();
		cy.get('.list-row-container:contains("Pending") .list-row-checkbox').click({
			multiple: true,
			force: true,
		});
		cy.get(".actions-btn-group button").contains("Actions").should("be.visible").click();
		cy.get(".dropdown-menu li:visible .dropdown-item")
			.should("have.length", 7)
			.each((el, index) => {
				cy.wrap(el).contains(actions[index]);
			})
			.then((elements) => {
				cy.intercept({
					method: "POST",
					url: "api/method/stylo.model.workflow.bulk_workflow_approval",
				}).as("bulk-approval");
				cy.wrap(elements).contains("Approve").click();
				cy.wait("@bulk-approval");
				cy.wait(300);
				cy.get_open_dialog().find(".btn-modal-close").click();
				cy.reload();
				cy.clear_filters();
				cy.get(".list-row-container:visible").should("contain", "Approved");
			});
	});
});
