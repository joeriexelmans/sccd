/* tslint:disable */
/* eslint-disable */
/**
* @param {any} out
* @returns {Handle}
*/
export function setup(out: any): Handle;
/**
* @param {Handle} h
* @param {number} delay
* @param {number} i
* @returns {RunUntilResult}
*/
export function add_event(h: Handle, delay: number, i: number): RunUntilResult;
/**
* @param {Handle} h
* @param {number} t
* @param {any} out
* @returns {RunUntilResult}
*/
export function run_until(h: Handle, t: number, out: any): RunUntilResult;
/**
*/
export enum InEvent {
  E_bottomLeftPressed,
  E_bottomLeftReleased,
  E_bottomRightPressed,
  E_bottomRightReleased,
  E_topLeftPressed,
  E_topLeftReleased,
  E_topRightPressed,
  E_topRightReleased,
  E_alarmStart,
  A0,
  A1,
  A2,
  A3,
  A4,
  A5,
  A6,
  A7,
  A8,
  A9,
  A10,
}
/**
*/
export enum OutEvent {
  E_setAlarm,
  E_setIndiglo,
  E_unsetIndiglo,
  E_increaseChronoByOne,
  E_resetChrono,
  E_refreshTimeDisplay,
  E_refreshAlarmDisplay,
  E_startSelection,
  E_stopSelection,
  E_selectNext,
  E_increaseSelection,
  E_refreshChronoDisplay,
  E_increaseTimeByOne,
  E_checkTime,
}
/**
*/
export class Handle {
  free(): void;
}
/**
*/
export class RunUntilResult {
  free(): void;
/**
* @returns {number}
*/
  at: number;
/**
* @returns {boolean}
*/
  reschedule: boolean;
/**
* @returns {number}
*/
  simtime: number;
}

export type InitInput = RequestInfo | URL | Response | BufferSource | WebAssembly.Module;

export interface InitOutput {
  readonly memory: WebAssembly.Memory;
  readonly __wbg_handle_free: (a: number) => void;
  readonly setup: (a: number) => number;
  readonly add_event: (a: number, b: number, c: number) => number;
  readonly __wbg_rununtilresult_free: (a: number) => void;
  readonly __wbg_get_rununtilresult_simtime: (a: number) => number;
  readonly __wbg_set_rununtilresult_simtime: (a: number, b: number) => void;
  readonly __wbg_get_rununtilresult_reschedule: (a: number) => number;
  readonly __wbg_set_rununtilresult_reschedule: (a: number, b: number) => void;
  readonly __wbg_get_rununtilresult_at: (a: number) => number;
  readonly __wbg_set_rununtilresult_at: (a: number, b: number) => void;
  readonly run_until: (a: number, b: number, c: number) => number;
}

/**
* If `module_or_path` is {RequestInfo} or {URL}, makes a request and
* for everything else, calls `WebAssembly.instantiate` directly.
*
* @param {InitInput | Promise<InitInput>} module_or_path
*
* @returns {Promise<InitOutput>}
*/
export default function init (module_or_path?: InitInput | Promise<InitInput>): Promise<InitOutput>;
        