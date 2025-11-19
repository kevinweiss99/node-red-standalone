width = 19.5;
length = 27.5;
thickness = 1.5;
bandWidth = 9.5;
lenseHole = 10.5;
bandHeight = 2.5;
$fn = 250;

/*
scale([1000, 1000, 1000])
translate([-0.28, -0.255, -1.16])
*import("head.stl", convexity=10);

sphere(d=215);
*/

module bottom() {
    difference() {
        cube([width + 2*thickness, length + 2*thickness, 5], true);
        translate([0, 0, -105])
        sphere(d=215);
        
        cube([2, 2*length, 10], true);
    }

    difference() {
        translate([0, 0, bandHeight / 2 + 3])
        cube([width + 2*thickness, length + 2*thickness, bandHeight + 1], true);
        
        translate([0, 0, bandHeight / 2 + 3])
        cube([bandWidth, 2*length, bandHeight], true);
        
        cube([2, 2*length, 10], true);
    }

    translate([0, 0, bandHeight - 2])
    difference() {
        translate([0, 0, 10])
        cube([width + 2*thickness, length + 2*thickness, 9], true);
        
        translate([0, 0, 10.5])
        cube([width, length, 9], true);
        
        translate([0, length / 2, 7.75])
        cube([8, length, 3.5], true);
        
        translate([0, length / 2, 12])
        cube([1.5, length, 6], true);
    }
}

module top() {
    difference() {
        union() {
            cube([width + 2*thickness, length + 2*thickness, thickness], true);
            translate([0, 0, -thickness])
            cube([width - 0.15, length - 0.15, thickness], true);
        }
        
        translate([0, 0, -5])
        cylinder(d1=lenseHole, d2=lenseHole, 10);
    }
    
    translate([0, length / 2 - 3, -3])
    cube([width - 5, 2, 2], true);
    
    translate([0, -length / 2 + 3, -3])
    cube([width - 5, 2, 2], true);
}

*bottom();
translate([0, 0, 20])
top();
