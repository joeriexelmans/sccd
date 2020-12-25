
export class OutputHandler {
  constructor(cb) {
    this.cb = cb;
  }

  handle_output(out_event) {
    this.cb(out_event);
  }
}