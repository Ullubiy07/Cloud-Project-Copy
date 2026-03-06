import { Box, HStack, Text, Button, useColorMode } from "@chakra-ui/react";

const Navbar = () => {
    const { colorMode } = useColorMode();

    return (
        <Box
            px={4}
            py={2}
            bg="gray.900"
            _light={{ bg: "gray.100" }}
            borderBottom="1px solid"
            borderColor={colorMode === "dark" ? "#2a2a35" : "gray.200"}
        >
            <HStack justifyContent="space-between">

                <Text fontWeight="700" fontSize="lg" letterSpacing="1px">
                    Cloud Editor
                </Text>

                <HStack spacing={2}>
                    <Button variant="outline" colorScheme="blue" size="sm">
                        Log In
                    </Button>
                    <Button variant="outline" colorScheme="blue" size="sm">
                        Sign Up
                    </Button>
                </HStack>

            </HStack>
        </Box>
    );
};
export default Navbar;