import "bootstrap";
import * as $ from "jquery";
import "./style.css";
import "bootstrap/dist/css/bootstrap.min.css";
import { WebRTCClient } from "./client";
import { MediaStreamScreen } from "./screen";

const canvas = <HTMLCanvasElement>document.getElementById("screen-canvas");
const screen = new MediaStreamScreen(canvas);
const client = new WebRTCClient(screen);


$(() => {
    $("#connect-modal :submit").on("click", async e => {
        const offer = $("#offer-area").val().toString();
        const answer = await client.SetOfferAndCreateAnswer(offer);
        $("#answer-area").val(answer);
    });
});