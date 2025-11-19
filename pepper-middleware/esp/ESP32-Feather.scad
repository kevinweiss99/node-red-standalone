width = 23.5;
height = 11;
length = 52;
usbWidth = 10;
usbHeight = 4;
thickness = 1;
$fn = 100;

module base() {
    difference() {
        cube([width + thickness*2, length + thickness*2, height + thickness], true);
        
        translate([0, 0, thickness * 1.5])
        cube([width, length, height + thickness * 2], true);
        
        translate([0, -length / 2 + thickness / 2, - height / 2 + 4.5])
        rotate([90, 0, 0])
        hull() {
            translate([-usbWidth * 0.35, 0, 0])
            cylinder(thickness * 2, usbHeight / 2, usbHeight / 2);
            
            translate([usbWidth * 0.35, 0, 0])
            cylinder(thickness * 2, usbHeight / 2, usbHeight / 2);
        }
        
        translate([0, -length / 2 - thickness / 2, height / 2])
        cube([4, thickness * 2, 2], true);
    }
}

module top() {
    cube([width + thickness*2, length + thickness*2, thickness], true);
    
    difference() {
        translate([0, 0, -thickness / 2 - 1 / 2])
        cube([width, length, 1], true);
        
        translate([0, -length / 2 + thickness / 2, -thickness / 2 - 1 / 2])
        cube([4, thickness * 2, 1.001], true);
    }
}

base();

translate([0, 0, height])
top();