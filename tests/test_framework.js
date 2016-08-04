function InputEvent(name, port, parameters, time_offset) {
	this.name = name;
	this.port = port;
	this.parameters = parameters;
	this.time_offset = time_offset;
}

TestFramework = {
	Results: function() {
		this.start_time = (new Date()).getTime();
		this.num_passed = 0;
		this.num_total = 0;
		this.num_skipped = 0;
	},
	LogResults: function(log, results) {
		var time = ((new Date()).getTime() - results.start_time);
		log(results.num_passed + " out of " + results.num_total + " tests passed, " + results.num_skipped + " skipped.");
		log("tests took " + time + " ms");
	},
	RunAll: function(tests) {
		var run_single_test = (function(log) {
			return function(name, run_next_callback, results) {
				if (!window[name]) {
					log("skipping test \"" + name + "\"");
					results.num_skipped++;
					if (run_next_callback) {
						run_next_callback(results);
					} else {
						TestFramework.LogResults(log, results);
					}
					return;
				} else {
					// log("initializing test \"" + name + "\"");
				}
				var controller = new (window[name].Controller)(new JsEventLoop());
				var listener = controller.addOutputListener("test_output");
				var inputs = window[name].Test.prototype.input_events;
				var expected = window[name].Test.prototype.expected_events;
				if (expected === undefined) expected = new Array();
				var expected_flattened = new Array();
				for (var slot in expected) {
					if (!expected.hasOwnProperty(slot)) continue;
					for (var event in expected[slot]) {
						if (!expected[slot].hasOwnProperty(event)) continue;
							expected_flattened.push(expected[slot][event])
					}
				}
				var check_output = (function(log, test_name, listener, expected, run_next_callback, results) {
					return function() {
						// log("checking output...");
						var passed = true;

						if (listener.queue.length !== expected.length) {
							log("error: output listener queue length (" + listener.queue.length + ") differs from expected length (" + expected.length + "). Expected: " + JSON.stringify(expected) + ", got: " + JSON.stringify(listener.queue));
							passed = false;
						} else {
							// iterate over expected output events
							for (var e in expected) {
								if (!expected.hasOwnProperty(e)) continue;

								var actual_name = listener.queue[e].name;
								var actual_port = listener.queue[e].port;
								var actual_parameters = listener.queue[e].parameters;
								var expected_name = expected[e].name;
								var expected_port = expected[e].port;
								var expected_parameters = expected[e].parameters;

								if (actual_name !== expected_name) {
									log("error: expected_name["+e+"]=\"" + expected_name + "\", actual_name["+e+"]=\"" + actual_name + "\"");
									passed = false;
								}
								if (actual_port !== expected_port) {
									log("error: expected_port["+e+"]=\"" + expected_port + "\", actual_port["+e+"]=\"" + actual_port + "\"");
									passed = false;
								}

								if (actual_parameters.length !== expected_parameters.length) {
									log("error: event ["+e+"] \"" + actual_name + "\": number of actual parameters (" + actual_parameters.length + ") doesn't match expected (" + expected_parameters.length + ")");
									passed = false;
								} else {
									// iterate over expected parameters
									for (var p in expected_parameters) {
										if (!expected_parameters.hasOwnProperty(p)) continue;
										var actual_parameter = actual_parameters[p];
										var expected_parameter = expected_parameters[p];
										if (actual_parameter !== expected_parameter) {
											log("error: event \"" + actual_name + "\": expected_parameter=\"" + expected_parameter + "\", actual_parameter=\"" + actual_parameter + "\"");
											passed = false;
										}
									}
								}
							}
						}
						results.num_total++;
						if (passed) {
							log("test \"" + test_name + "\" passed.");
							results.num_passed++;
						} else {
							log("test \"" + test_name + "\" failed.");
						}

						// run next test
						if (run_next_callback)
							run_next_callback(results);
						else {
							TestFramework.LogResults(log, results);
						}
					};
				})(log, name, listener, expected_flattened, run_next_callback, results);

				for (var i in inputs) {
					if (!inputs.hasOwnProperty(i)) continue;
					ii = inputs[i]
					controller.addInput(new Event(ii.name, ii.port, ii.parameters), ii.time_offset);
				}

				// log("starting controller...");
				controller.finished_callback = check_output;
				controller.start();
			};
		})(log);

		var last = null;
		for (var t in tests) {
			if (!tests.hasOwnProperty(t)) continue;
			last = (function(name, callback) {
					return function(results) {
						run_single_test(name, callback, results);
					};
				})(tests[t], last);
		}
		var results = new (this.Results)();
		last(results);
	}
};
