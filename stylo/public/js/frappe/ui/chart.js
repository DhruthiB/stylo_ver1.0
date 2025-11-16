import { Chart } from "stylo-charts/dist/stylo-charts.esm";

stylo.provide("stylo.ui");
stylo.Chart = Chart;

stylo.ui.RealtimeChart = class RealtimeChart extends stylo.Chart {
	constructor(element, socketEvent, maxLabelPoints = 8, data) {
		super(element, data);
		if (data.data.datasets[0].values.length > maxLabelPoints) {
			stylo.throw(
				__(
					"Length of passed data array is greater than value of maximum allowed label points!"
				)
			);
		}
		this.currentSize = data.data.datasets[0].values.length;
		this.socketEvent = socketEvent;
		this.maxLabelPoints = maxLabelPoints;

		this.start_updating = function () {
			stylo.realtime.on(this.socketEvent, (data) => {
				this.update_chart(data.label, data.points);
			});
		};

		this.stop_updating = function () {
			stylo.realtime.off(this.socketEvent);
		};

		this.update_chart = function (label, data) {
			if (this.currentSize >= this.maxLabelPoints) {
				this.removeDataPoint(0);
			} else {
				this.currentSize++;
			}
			this.addDataPoint(__(label), data);
		};
	}
};
