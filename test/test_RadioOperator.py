import unittest

from core import RadioOperator, Heading, Restraints, Sonar, Drone, Hit, Surface
from enums.direction import direction
from enums.codes import codes


class TestRadioOperator(unittest.TestCase):
    
    def test_execute_direction(self):
        
        operator: RadioOperator = RadioOperator()
        
        args: list[str] = ["north"]
        code: codes = operator.append_heading(args)
        self.assertEqual(code, codes.HEADING_ADDED, "Return code should be HEADING_ADDED")
        self.assertEqual(direction.NORTH, operator._route[-1].d, "Direction not north")
        self.assertEqual(1, len(operator._route), "Route should only have 1 heading")
        
        north_heading: Heading = operator._route[-1]
        
        args = ["east"]
        code = operator.append_heading(args)
        self.assertEqual(code, codes.HEADING_ADDED, "Return code should be HEADING_ADDED")
        self.assertIs(north_heading, operator._route[0], "Firt heading should remain the same")
        self.assertEqual(direction.EAST, operator._route[-1].d, "Direction not east")
        self.assertEqual(2, len(operator._route), "Route should only have 2 headings")
        
        east_heading: Heading = operator._route[-1]
        
        args = ["south"]
        code = operator.append_heading(args)
        self.assertEqual(code, codes.HEADING_ADDED, "Return code should be HEADING_ADDED")
        self.assertIs(north_heading, operator._route[0], "Firt heading should remain the same")
        self.assertIs(east_heading, operator._route[1], "Second heading should remain the same")
        self.assertEqual(direction.SOUTH, operator._route[-1].d, "Direction not south")
        self.assertEqual(3, len(operator._route), "Route should only have 3 headings")
        
        south_heading: Heading = operator._route[-1]
        
        args = ["west"]
        code = operator.append_heading(args)
        self.assertEqual(codes.INTERSECTING_PATH, code, "Route shouldn't be allowed to intersect")
        self.assertIs(north_heading, operator._route[0], "Firt heading should remain the same")
        self.assertIs(east_heading, operator._route[1], "Second heading should remain the same")
        self.assertIs(south_heading, operator._route[2], "Third heading should remain the same")
        self.assertEqual(3, len(operator._route), "Route should only have 3 headings")
        
        args = ["south"]
        code = operator.append_heading(args)
        self.assertEqual(code, codes.HEADING_ADDED, "Return code should be HEADING_ADDED")
        self.assertIs(north_heading, operator._route[0], "Firt heading should remain the same")
        self.assertIs(east_heading, operator._route[1], "Second heading should remain the same")
        self.assertIs(south_heading, operator._route[2], "Third heading should remain the same")
        self.assertEqual(direction.SOUTH, operator._route[-1].d, "Direction not south")
        self.assertEqual(4, len(operator._route), "Route should only have 4 headings")
        
        south2_heading: Heading = operator._route[-1]
        
        args = ["west"]
        code = operator.append_heading(args)
        self.assertEqual(code, codes.HEADING_ADDED, "Return code should be HEADING_ADDED")
        self.assertIs(north_heading, operator._route[0], "Firt heading should remain the same")
        self.assertIs(east_heading, operator._route[1], "Second heading should remain the same")
        self.assertIs(south_heading, operator._route[2], "Third heading should remain the same")
        self.assertIs(south2_heading, operator._route[3], "Fourth heading should remain the same")
        self.assertEqual(direction.WEST, operator._route[-1].d, "Direction not west")
        self.assertEqual(5, len(operator._route), "Route should only have 5 headings")
        
        
    def test_execute_sonar(self):
        operator: RadioOperator = RadioOperator()
        
        # Test the special case of the starting position
        for row_text in ("row", "r"):
            for column_text in ("column", "col", "c"):
                operator.reset_route()
                
                args = [row_text + "-1", column_text + "-A"]
                code: codes = operator.execute_sonar(args)
                self.assertEqual(code, codes.SONAR_ADDED, "Incorrect code returned")
                self.assertEqual(len(operator._route), 0, "There shouldn't be any headings")
                self.assertEqual(len(operator._starting_restraints._sonar), 1, "One sonar restraint should exist")
                self.assertEqual(operator._starting_restraints._sonar[0].col, 0, "Column value incorrect")
                self.assertEqual(operator._starting_restraints._sonar[0].row, 0, "Row value incorrect")
                self.assertEqual(operator._starting_restraints._sonar[0].sec, -1, "Sector value incorrect")
                
                first_sonar: Sonar = operator._starting_restraints._sonar[0]
                
                args = [column_text + "-B", row_text + "-2"]
                code = operator.execute_sonar(args)
                self.assertEqual(code, codes.SONAR_ADDED, "Incorrect code returned")
                self.assertEqual(len(operator._route), 0, "There shouldn't be any headings")
                self.assertEqual(len(operator._starting_restraints._sonar), 2, "Two sonar restraints should exist")
                self.assertIs(first_sonar, operator._starting_restraints._sonar[0], "First sonar restraint should remain the same")
                self.assertEqual(operator._starting_restraints._sonar[1].col, 1, "Column value incorrect")
                self.assertEqual(operator._starting_restraints._sonar[1].row, 1, "Row value incorrect")
                self.assertEqual(operator._starting_restraints._sonar[1].sec, -1, "Sector value incorrect")
        
        for row_text in ("row", "r"):
            for sector_text in ("sector", "sec", "s"):
                operator.reset_route()
                
                args = ["north"]
                operator.append_heading(args)
                
                args = [row_text + "-1", sector_text + "-1"]
                code: codes = operator.execute_sonar(args)
                self.assertEqual(code, codes.SONAR_ADDED, "Icorrect code returned")
                self.assertEqual(len(operator._route), 1, "There should only be one heading")
                self.assertEqual(len(operator._route[0].restraints._sonar), 1, "There should only be one sonar restraint")
                self.assertEqual(operator._route[0].restraints._sonar[0].col, -1, "Column value incorrect")
                self.assertEqual(operator._route[0].restraints._sonar[0].row, 0, "Row value incorrect")
                self.assertEqual(operator._route[0].restraints._sonar[0].sec, 1, "Sector value incorrect")
                
                first_sonar: Sonar = operator._route[0].restraints._sonar[0]
                
                args = [sector_text + "-2", row_text + "-2"]
                code = operator.execute_sonar(args)
                self.assertEqual(code, codes.SONAR_ADDED, "Incorrect code returned")
                self.assertEqual(len(operator._route), 1, "there should only be one heading")
                self.assertEqual(len(operator._route[0].restraints._sonar), 2, "There should only be two sonar restraints")
                self.assertIs(operator._route[0].restraints._sonar[0], first_sonar, "First sonar restraint should remain the same")
                self.assertEqual(operator._route[0].restraints._sonar[1].col, -1, "Column value incorrect")
                self.assertEqual(operator._route[0].restraints._sonar[1].row, 1, "Row value incorrect")
                self.assertEqual(operator._route[0].restraints._sonar[1].sec, 2, "Sector value incorrect")
        
        for column_text in ("column", "col", "c"):
            for sector_text in ("sector", "sec", "s"):
                operator.reset_route()
                
                args = ["north"]
                operator.append_heading(args)
                operator.append_heading(args)
                
                args = [column_text + "-C", sector_text + "-3"]
                code: codes = operator.execute_sonar(args)
                self.assertEqual(code, codes.SONAR_ADDED, "Icorrect code returned")
                self.assertEqual(len(operator._route), 2, "There should only be two headings")
                self.assertEqual(len(operator._route[1].restraints._sonar), 1, "There should only be one sonar restraint")
                self.assertEqual(operator._route[1].restraints._sonar[0].col, 2, "Column value incorrect")
                self.assertEqual(operator._route[1].restraints._sonar[0].row, -1, "Row value incorrect")
                self.assertEqual(operator._route[1].restraints._sonar[0].sec, 3, "Sector value incorrect")
                
                first_sonar: Sonar = operator._route[1].restraints._sonar[0]
                
                args = [sector_text + "-4", column_text + "-D"]
                code = operator.execute_sonar(args)
                self.assertEqual(code, codes.SONAR_ADDED, "Incorrect code returned")
                self.assertEqual(len(operator._route), 2, "there should only be two headings")
                self.assertEqual(len(operator._route[1].restraints._sonar), 2, "There should only be two sonar restraints")
                self.assertIs(operator._route[1].restraints._sonar[0], first_sonar, "First sonar restraint should remain the same")
                self.assertEqual(operator._route[1].restraints._sonar[1].col, 3, "Column value incorrect")
                self.assertEqual(operator._route[1].restraints._sonar[1].row, -1, "Row value incorrect")
                self.assertEqual(operator._route[1].restraints._sonar[1].sec, 4, "Sector value incorrect")
        
    def test_execute_drone(self):
        operator: RadioOperator = RadioOperator()
        
        args: list[str] = ["5", "true"]
        code: codes = operator.execute_drone(args)
        self.assertEqual(code, codes.DRONE_ADDED, "Incorrect code returned")
        self.assertEqual(len(operator._route), 0, "There should be no headings")
        self.assertEqual(len(operator._starting_restraints._drone), 1, "There should only be one drone restraint")
        self.assertEqual(operator._starting_restraints._drone[0].valid, True, "Boolean value incorrect")
        self.assertEqual(operator._starting_restraints._drone[0].sec, 5, "Sector value incorrect")
        
        first_drone: Drone = operator._starting_restraints._drone[0]
        
        args = ["6", "false"]
        code = operator.execute_drone(args)
        self.assertEqual(code, codes.DRONE_ADDED, "Incorrect code returned")
        self.assertEqual(len(operator._route), 0, "There should be no headings")
        self.assertEqual(len(operator._starting_restraints._drone), 2, "There should only be two drone restraints")
        self.assertIs(operator._starting_restraints._drone[0], first_drone, "First drone restraint should remain the same")
        self.assertEqual(operator._starting_restraints._drone[1].valid, False, "Boolean value incorrect")
        self.assertEqual(operator._starting_restraints._drone[1].sec, 6, "Sector value incorrect")
        
        args = ["north"]
        operator.append_heading(args)
        
        args = ["1", "true"]
        code = operator.execute_drone(args)
        self.assertEqual(code, codes.DRONE_ADDED, "Incorrect code returned")
        self.assertEqual(len(operator._route), 1, "There should only be one heading")
        self.assertEqual(len(operator._route[0].restraints._drone), 1, "There should only be one drone restraint")
        self.assertEqual(operator._route[0].restraints._drone[0].valid, True, "Boolean value incorrect")
        self.assertEqual(operator._route[0].restraints._drone[0].sec, 1, "Sector value incorrect")
        
        first_drone = operator._route[0].restraints._drone[0]
        
        args = ["9", "false"]
        code = operator.execute_drone(args)
        self.assertEqual(code, codes.DRONE_ADDED, "Incorrect code returned")
        self.assertEqual(len(operator._route), 1, "There should only be one heading")
        self.assertEqual(len(operator._route[0].restraints._drone), 2, "There should only be two drone restraints")
        self.assertEqual(operator._route[0].restraints._drone[1].valid, False, "Boolean value incorrect")
        self.assertEqual(operator._route[0].restraints._drone[1].sec, 9, "Sector value incorrect")
        
    def test_execute_hit(self):
        ...
        
    #def test_execute_surface(self):
    #    ...