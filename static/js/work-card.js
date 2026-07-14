function workCard(options) {
    options = options || {};
    return {
        hasInlineVideo: !!options.inlineVideo,
        youtubePreviewUrl: options.youtubePreviewUrl || '',
        pinned: false,
        hovering: false,
        playing: false,
        get hasPreview() {
            return this.hasInlineVideo || !!this.youtubePreviewUrl;
        },
        get video() {
            return this.$refs.video || null;
        },
        playInline() {
            if (!this.video) return;
            this.video.play().catch(function () {});
        },
        pauseInline(reset) {
            if (!this.video) return;
            this.video.pause();
            if (reset) {
                this.video.currentTime = 0;
            }
        },
        onEnter() {
            this.hovering = true;
            if (this.pinned) return;
            if (this.hasInlineVideo) {
                this.playInline();
                return;
            }
            if (this.youtubePreviewUrl) {
                this.playing = true;
            }
        },
        onLeave() {
            this.hovering = false;
            if (this.pinned) return;
            if (this.hasInlineVideo) {
                this.pauseInline(true);
                return;
            }
            if (this.youtubePreviewUrl) {
                this.playing = false;
            }
        },
        togglePin() {
            if (!this.hasPreview) return;
            this.pinned = !this.pinned;
            if (this.pinned) {
                if (this.hasInlineVideo) {
                    this.playInline();
                } else if (this.youtubePreviewUrl) {
                    this.playing = true;
                }
            } else {
                if (this.hasInlineVideo) {
                    this.pauseInline(true);
                } else if (this.youtubePreviewUrl) {
                    this.playing = false;
                }
            }
        },
    };
}
