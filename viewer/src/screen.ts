import { InputReport, ScreenEvent, MouseMoveEvent, MouseButtonEvent, MouseButtonKind, ButtonEventKind } from "./models";


export class MediaStreamScreen {

    public readonly SendReportInterval: number = 100;

    public readonly MouseMoveThrottleTime: number = 50;

    private canvas: HTMLCanvasElement;

    private ctx: CanvasRenderingContext2D;

    private video: HTMLVideoElement;

    private dataChannel: RTCDataChannel = null;

    private mediaStream: MediaStream = null;

    private started: boolean = false;

    private sendReportIntervalId: number;

    private eventQueue: ScreenEvent[] = [];

    private mouseMoveThrottle: number = null;

    constructor(canvas: HTMLCanvasElement) {
        this.canvas = canvas;
        this.ctx = canvas.getContext("2d");

        this.canvas.addEventListener("mousedown", this.canvasMouseDown);
        this.canvas.addEventListener("mouseup", this.canvasMouseUp);
        this.canvas.addEventListener("mousemove", this.canvasMouseMove);
        this.canvas.addEventListener("contextmenu", (e) => {
            e.preventDefault();
        });

        // NOTE(igarashi): create a video element to render stream
        this.video = document.createElement("video");
        this.video.onresize = (e) => {
            this.updateCanvasSize();
        };

        this.video.onloadedmetadata = () => {
            this.video.play();
            this.updateCanvasSize();
            this.updateFrameByVideo();
        };
    }

    private sendReport = () => {
        const toSend = this.eventQueue.splice(0, this.eventQueue.length);
        if (this.dataChannel == null || this.dataChannel.readyState !== "open")
            return;

        if (toSend.length == 0) return;

        const report = new InputReport(toSend);
        const json = JSON.stringify(report);
        this.dataChannel.send(json);
    }

    private getScreenPixel = (e: MouseEvent): { x: number, y: number } => {
        const rect = (<HTMLElement>e.target).getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        return { x: (x / rect.width) * this.canvas.width, y: (y / rect.height) * this.canvas.height };
    }

    private getMouseButtonKind(e: MouseEvent): MouseButtonKind {
        switch (e.button) {
            case 0:
                return MouseButtonKind.Left;
            case 1:
                return MouseButtonKind.Middle;
            case 2:
                return MouseButtonKind.Right;
            default:
                return MouseButtonKind.Left;
        }
    }

    private canvasMouseDown = (e: MouseEvent) => {
        if (!this.started) return;

        const { x, y } = this.getScreenPixel(e);
        this.eventQueue.push(new MouseMoveEvent(x, y));
        this.eventQueue.push(new MouseButtonEvent(this.getMouseButtonKind(e), ButtonEventKind.ButtonDown));
    }

    private canvasMouseUp = (e: MouseEvent) => {
        if (!this.started) return;

        const { x, y } = this.getScreenPixel(e);
        this.eventQueue.push(new MouseMoveEvent(x, y));
        this.eventQueue.push(new MouseButtonEvent(this.getMouseButtonKind(e), ButtonEventKind.ButtonUp));
    }

    private canvasMouseMove = (e: MouseEvent) => {
        if (!this.started) return;

        if (this.mouseMoveThrottle != null)
            return;

        this.mouseMoveThrottle = window.setTimeout(() => {
            this.mouseMoveThrottle = null;
        }, this.MouseMoveThrottleTime);
        const { x, y } = this.getScreenPixel(e);
        this.eventQueue.push(new MouseMoveEvent(x, y));
    }

    private updateFrameByVideo = () => {
        this.ctx.drawImage(this.video, 0, 0);
        window.requestAnimationFrame(this.updateFrameByVideo);
    }

    private updateCanvasSize() {
        this.canvas.width = this.video.videoWidth;
        this.canvas.height = this.video.videoHeight;
    }

    public SetupMediaStream(stream: MediaStream) {
        this.mediaStream = stream;
        this.video.srcObject = stream;
    }

    public SetupDataChannel(channel: RTCDataChannel) {
        this.dataChannel = channel;
    }

    public StartReport = () => {
        if (this.started)
            return;
        this.started = true;
        this.sendReportIntervalId = window.setInterval(() => {
            this.sendReport();
        }, this.SendReportInterval);
    }

    public StopReport = () => {
        if (!this.started)
            return;

        this.dataChannel = null;
        this.mediaStream = null;
        window.clearInterval(this.sendReportIntervalId);
        this.started = false;
    }

}
