import { InputReport, ScreenEvent } from "./models";


export class MediaStreamScreen {

    public readonly SendReportInterval: number = 100;

    private canvas: HTMLCanvasElement;

    private ctx: CanvasRenderingContext2D;

    private video: HTMLVideoElement;

    private dataChannel: RTCDataChannel = null;

    private mediaStream: MediaStream = null;

    private started: boolean = false;

    private sendReportIntervalId: number;

    private eventQueue: ScreenEvent[] = [];

    constructor(canvas: HTMLCanvasElement) {
        this.canvas = canvas;
        this.ctx = canvas.getContext("2d");

        this.canvas.addEventListener("click", this.canvasClicked);

        // NOTE(igarashi): create a video element to render stream
        this.video = document.createElement("video");
        this.video.onresize = (e) => {
            this.updateCanvasSize();
        }

        this.video.onloadedmetadata = () => {
            this.video.play();
            this.updateCanvasSize();
            this.updateFrameByVideo();
        }
    }

    private sendReport = () => {
        const toSend = this.eventQueue.splice(0, this.eventQueue.length);
        if (this.dataChannel == null || this.dataChannel.readyState !== "open")
            return;

        const report = new InputReport()
        report.events = toSend;

        const json = JSON.stringify(report);
        this.dataChannel.send(json);
    }

    private canvasClicked = (e: MouseEvent) => {
        if (!this.started) return;

        const rect = (<HTMLElement>e.target).getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const screenX = (x / rect.width) * this.canvas.width;
        const screenY = (y / rect.height) * this.canvas.height;

        console.log(`${screenX}, ${screenY}`);
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
