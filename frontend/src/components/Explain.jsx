import {
    Modal, ModalOverlay, ModalContent, ModalHeader, ModalBody,
    ModalCloseButton, Text, Spinner, Box,
} from "@chakra-ui/react";

const Explain = ({ isOpen, onClose, explanation, loading }) => {
    return (
        <Modal isOpen={isOpen} onClose={onClose} size="xl" scrollBehavior="inside">
            <ModalOverlay />
            <ModalContent bg="gray.800">
                <ModalHeader color="white">Code Explanation</ModalHeader>
                <ModalCloseButton color="white" />
                <ModalBody pb={6}>
                    {loading && (
                        <Box display="flex" justifyContent="center" py={8}>
                            <Spinner size="lg" color="green.400" />
                        </Box>
                    )}
                    {!loading && explanation && (
                        <Text color="gray.100" whiteSpace="pre-wrap" fontSize="sm">
                            {explanation}
                        </Text>
                    )}
                </ModalBody>
            </ModalContent>
        </Modal>
    );
};

export default Explain;