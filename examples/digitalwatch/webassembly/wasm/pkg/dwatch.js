
let wasm;

let cachedTextDecoder = new TextDecoder('utf-8', { ignoreBOM: true, fatal: true });

cachedTextDecoder.decode();

let cachegetUint8Memory0 = null;
function getUint8Memory0() {
    if (cachegetUint8Memory0 === null || cachegetUint8Memory0.buffer !== wasm.memory.buffer) {
        cachegetUint8Memory0 = new Uint8Array(wasm.memory.buffer);
    }
    return cachegetUint8Memory0;
}

function getStringFromWasm0(ptr, len) {
    return cachedTextDecoder.decode(getUint8Memory0().subarray(ptr, ptr + len));
}

const heap = new Array(32).fill(undefined);

heap.push(undefined, null, true, false);

function getObject(idx) { return heap[idx]; }

let stack_pointer = 32;

function addBorrowedObject(obj) {
    if (stack_pointer == 1) throw new Error('out of js stack');
    heap[--stack_pointer] = obj;
    return stack_pointer;
}
/**
* @param {any} out
* @returns {Handle}
*/
export function setup(out) {
    try {
        var ret = wasm.setup(addBorrowedObject(out));
        return Handle.__wrap(ret);
    } finally {
        heap[stack_pointer++] = undefined;
    }
}

function _assertClass(instance, klass) {
    if (!(instance instanceof klass)) {
        throw new Error(`expected instance of ${klass.name}`);
    }
    return instance.ptr;
}
/**
* @param {Handle} h
* @param {number} delay
* @param {number} i
* @returns {RunUntilResult}
*/
export function add_event(h, delay, i) {
    _assertClass(h, Handle);
    var ret = wasm.add_event(h.ptr, delay, i);
    return RunUntilResult.__wrap(ret);
}

/**
* @param {Handle} h
* @param {number} t
* @param {any} out
* @returns {RunUntilResult}
*/
export function run_until(h, t, out) {
    try {
        _assertClass(h, Handle);
        var ret = wasm.run_until(h.ptr, t, addBorrowedObject(out));
        return RunUntilResult.__wrap(ret);
    } finally {
        heap[stack_pointer++] = undefined;
    }
}

/**
*/
export const InEvent = Object.freeze({ E_bottomLeftPressed:0,"0":"E_bottomLeftPressed",E_bottomLeftReleased:1,"1":"E_bottomLeftReleased",E_bottomRightPressed:2,"2":"E_bottomRightPressed",E_bottomRightReleased:3,"3":"E_bottomRightReleased",E_topLeftPressed:4,"4":"E_topLeftPressed",E_topLeftReleased:5,"5":"E_topLeftReleased",E_topRightPressed:6,"6":"E_topRightPressed",E_topRightReleased:7,"7":"E_topRightReleased",E_alarmStart:8,"8":"E_alarmStart",A0:9,"9":"A0",A1:10,"10":"A1",A2:11,"11":"A2",A3:12,"12":"A3",A4:13,"13":"A4",A5:14,"14":"A5",A6:15,"15":"A6",A7:16,"16":"A7",A8:17,"17":"A8",A9:18,"18":"A9",A10:19,"19":"A10", });
/**
*/
export const OutEvent = Object.freeze({ E_setAlarm:0,"0":"E_setAlarm",E_setIndiglo:1,"1":"E_setIndiglo",E_unsetIndiglo:2,"2":"E_unsetIndiglo",E_increaseChronoByOne:3,"3":"E_increaseChronoByOne",E_resetChrono:4,"4":"E_resetChrono",E_refreshTimeDisplay:5,"5":"E_refreshTimeDisplay",E_refreshAlarmDisplay:6,"6":"E_refreshAlarmDisplay",E_startSelection:7,"7":"E_startSelection",E_stopSelection:8,"8":"E_stopSelection",E_selectNext:9,"9":"E_selectNext",E_increaseSelection:10,"10":"E_increaseSelection",E_refreshChronoDisplay:11,"11":"E_refreshChronoDisplay",E_increaseTimeByOne:12,"12":"E_increaseTimeByOne",E_checkTime:13,"13":"E_checkTime", });
/**
*/
export class Handle {

    static __wrap(ptr) {
        const obj = Object.create(Handle.prototype);
        obj.ptr = ptr;

        return obj;
    }

    free() {
        const ptr = this.ptr;
        this.ptr = 0;

        wasm.__wbg_handle_free(ptr);
    }
}
/**
*/
export class RunUntilResult {

    static __wrap(ptr) {
        const obj = Object.create(RunUntilResult.prototype);
        obj.ptr = ptr;

        return obj;
    }

    free() {
        const ptr = this.ptr;
        this.ptr = 0;

        wasm.__wbg_rununtilresult_free(ptr);
    }
    /**
    * @returns {number}
    */
    get simtime() {
        var ret = wasm.__wbg_get_rununtilresult_simtime(this.ptr);
        return ret >>> 0;
    }
    /**
    * @param {number} arg0
    */
    set simtime(arg0) {
        wasm.__wbg_set_rununtilresult_simtime(this.ptr, arg0);
    }
    /**
    * @returns {boolean}
    */
    get reschedule() {
        var ret = wasm.__wbg_get_rununtilresult_reschedule(this.ptr);
        return ret !== 0;
    }
    /**
    * @param {boolean} arg0
    */
    set reschedule(arg0) {
        wasm.__wbg_set_rununtilresult_reschedule(this.ptr, arg0);
    }
    /**
    * @returns {number}
    */
    get at() {
        var ret = wasm.__wbg_get_rununtilresult_at(this.ptr);
        return ret >>> 0;
    }
    /**
    * @param {number} arg0
    */
    set at(arg0) {
        wasm.__wbg_set_rununtilresult_at(this.ptr, arg0);
    }
}

async function load(module, imports) {
    if (typeof Response === 'function' && module instanceof Response) {

        if (typeof WebAssembly.instantiateStreaming === 'function') {
            try {
                return await WebAssembly.instantiateStreaming(module, imports);

            } catch (e) {
                if (module.headers.get('Content-Type') != 'application/wasm') {
                    console.warn("`WebAssembly.instantiateStreaming` failed because your server does not serve wasm with `application/wasm` MIME type. Falling back to `WebAssembly.instantiate` which is slower. Original error:\n", e);

                } else {
                    throw e;
                }
            }
        }

        const bytes = await module.arrayBuffer();
        return await WebAssembly.instantiate(bytes, imports);

    } else {

        const instance = await WebAssembly.instantiate(module, imports);

        if (instance instanceof WebAssembly.Instance) {
            return { instance, module };

        } else {
            return instance;
        }
    }
}

async function init(input) {
    if (typeof input === 'undefined') {
        input = import.meta.url.replace(/\.js$/, '_bg.wasm');
    }
    const imports = {};
    imports.wbg = {};
    imports.wbg.__wbg_handleoutput_70a5b58d88cc044e = function(arg0, arg1) {
        getObject(arg0).handle_output(arg1 >>> 0);
    };
    imports.wbg.__wbindgen_throw = function(arg0, arg1) {
        throw new Error(getStringFromWasm0(arg0, arg1));
    };

    if (typeof input === 'string' || (typeof Request === 'function' && input instanceof Request) || (typeof URL === 'function' && input instanceof URL)) {
        input = fetch(input);
    }

    const { instance, module } = await load(await input, imports);

    wasm = instance.exports;
    init.__wbindgen_wasm_module = module;

    return wasm;
}

export default init;

