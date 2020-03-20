

export class MediaStreamScreen {

    private canvas: HTMLCanvasElement;

    private ctx: CanvasRenderingContext2D;

    private video: HTMLVideoElement;

    private dataChannel: RTCDataChannel = null;

    private mediaStream: MediaStream = null;

    constructor(canvas: HTMLCanvasElement) {
        this.canvas = canvas;
        this.ctx = canvas.getContext("2d");

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

    private updateCanvasSize() {
        this.canvas.width = this.video.videoWidth;
        this.canvas.height = this.video.videoHeight;
    }

    private updateFrameByVideo() {
        this.ctx.drawImage(this.video, 0, 0);
        window.requestAnimationFrame(this.updateFrameByVideo);
    }

    public SetupMediaStream(stream: MediaStream) {
        this.mediaStream = stream;
        this.video.srcObject = stream;
    }

    public SetupDataChannel(channel: RTCDataChannel) {
        this.dataChannel = channel;
    }

}