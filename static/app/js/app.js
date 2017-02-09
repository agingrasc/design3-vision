(function() {
    "use strict";

    var imageCount = document.getElementById("imageCount");

    var CalibrationImagesListView = {
        el: document.getElementById('calibrationImagesListView'),

        render: function(images) {
            imageCount.innerText = images.length.toString();
            for (var i = 0; i < images.length; i++) {
                var currentImagePath = images[i];
                var listElement = createImageListElement(currentImagePath);
                this.el.appendChild(listElement);
            }
        }
    };

    var CurrentImageView = {
        el: document.getElementById('currentImageView'),

        init: function() {
            this.el.addEventListener('click', function(event) {
                event.preventDefault();

                var boundingRect = this.el.getBoundingClientRect();
                var position = {
                    x: event.x,
                    y: event.y
                };

                console.log(getPositionRelativeTo(position, boundingRect));
            }.bind(this));
        },

        updateImage: function(imagePath) {
            this.render(imagePath);
        },

        render: function(image) {
            window.requestAnimationFrame(function() {
                this.el.src = image.src;
            }.bind(this));
        }
    };

    var ClickView = {
        el: document.getElementById('clickView'),

        render: function(position) {
            this.el.innerText = "(" + position.x.toString() + ", " + position.y.toString() + ")";
        }
    };

    var MainController = {
        init: function(images) {
            CalibrationImagesListView.render(images.calibration.images);

            CurrentImageView.render(images.calibration.images[0]);
        }
    };

    var ImageService = {
        getImagesInfos: function(callback) {
            var imagesInfosRequest = new XMLHttpRequest();
            imagesInfosRequest.onload = function(event) {
                callback(JSON.parse(event.target.response));
            };
            imagesInfosRequest.open("GET", 'http://localhost:5000/images-infos');
            imagesInfosRequest.send();
        }
    };

    function getPositionRelativeTo(cursorPosition, boundingRect) {
        return {
            x: cursorPosition.x - boundingRect.left,
            y: cursorPosition.y - boundingRect.top
        };
    }

    function createImageListElement(image) {
        var imageListElement = document.createElement("button");
        imageListElement.classList.add('list-group-item');
        imageListElement.innerText = image.name;
        imageListElement.addEventListener('click', function onClick(event) {
            event.preventDefault();

            CurrentImageView.render(image);
        });
        return imageListElement;
    }

    CurrentImageView.init();

    window.addEventListener('mousemove', function(event) {
        if (event.target === CurrentImageView.el) {
            var boundingRect = event.target.getBoundingClientRect();
            var position = {
                x: event.x,
                y: event.y
            };

            ClickView.render(getPositionRelativeTo(position, boundingRect));
        }
    });

    ImageService.getImagesInfos(MainController.init);
}());
