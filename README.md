# Ablation Spot Placer

This GUI-featuring application allows placement of black or white circles on .tif files received by CL imaging on SEM model: JEOL JSM-6610LV. Through OCR and CV the program reads the scalebar and determines the pixel radii of circles representing laser ablation spots of 30 micrometers in diameter.

Images are loaded as groups which represent directories received from the SEM. The user is able to switch between images, place circles of white or black color, undo his last placement or reset all placements on the active image. Finally by pressing the "CREATE PDF" button a .pdf file showing three columns of correctly labeled, enumerated and sorted groups of edited images is generated in a directory specified by the user.

## Prerequisites

This program is a Python script using the following libraries:
```
tkinter
```
```
PIL
```
```
cv2
```
```
pytesseract
```
```
reportlab
```

## Authors

* **Kosta Crnobrnja** - [crnobrnjak](https://github.com/crnobrnjak)

## License

This project is licensed under the GPL 3.0 License - see the [LICENSE.md](LICENSE.md) file for details
