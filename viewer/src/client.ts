import { MediaStreamScreen } from "./screen";


export class WebRTCClient {

    private pc: RTCPeerConnection;

    private screen: MediaStreamScreen;

    constructor(screen: MediaStreamScreen) {
        this.screen = screen;

        this.pc = new RTCPeerConnection({
            iceServers: [
                {
                    urls: "stun:stun.l.google.com:19302",
                }
            ]
        });
        this.pc.ontrack = this.onTrack.bind(this);
        this.pc.ondatachannel = this.onDataChannel.bind(this);
        this.pc.onconnectionstatechange = (e) => {
            switch (this.pc.iceConnectionState) {
                case "closed":
                case "failed":
                    this.pc.close();
                    alert("Connection has closed");
            }
        }
    }

    private onTrack(event: RTCTrackEvent): void {
        const streams = event.streams;
        if (streams.length !== 1) {
            console.error("len(streams) > 1");
            return;
        }

        const stream = streams[0];
        stream.onremovetrack = (e) => {
            alert("Disconnected");
        };
        this.screen.SetupMediaStream(stream);
    }

    private onDataChannel(event: RTCDataChannelEvent): void {
        const channel = event.channel;
        if (channel.label !== "io") {
            console.error(`Unknown datachannel opened: ${channel.label}`);
            return;
        }

        channel.onclose = (e) => {
            this.screen.StopReport();
        };

        this.screen.SetupDataChannel(channel);
        this.screen.StartReport();
    }

    public async SetOfferAndCreateAnswer(offer: string): Promise<string> {
        await this.pc.setRemoteDescription(new RTCSessionDescription(JSON.parse(offer)));
        const answer = await this.pc.createAnswer();

        // NOTE(igarashi): Create promise to wait until localDescription gets ready.
        var promise = new Promise<RTCSessionDescription>((resolve, reject) => {
            this.pc.onicecandidate = event => {
                if (event.candidate === null) {
                    resolve(this.pc.localDescription);
                    return;
                }
            };
        });

        await this.pc.setLocalDescription(answer);
        const localDescription = await promise;
        return JSON.stringify(localDescription);
    }

}
