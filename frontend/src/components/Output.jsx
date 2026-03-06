import { Box, useColorMode } from "@chakra-ui/react";

const Output = () => {
    const { colorMode } = useColorMode();

    return (
        <Box
            flex={1}
            p={2}
            border="1px solid"
            borderRadius={10}
            borderColor={colorMode === "dark" ? "#333" : "gray.200"}
            color={colorMode === "dark" ? "white" : "black"}
            overflow="auto"
        >
            Test
        </Box>
    );
};
export default Output;